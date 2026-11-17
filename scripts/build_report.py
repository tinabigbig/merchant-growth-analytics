# Builds docs/index.html (the report) from the dbt marts. Numbers come only from the marts.
import json, duckdb
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
c = duckdb.connect(str(ROOT / "data" / "olist.duckdb"), read_only=True)
def q(sql): return c.execute(sql).fetchall()

new_sellers = """seller_id not in (select seller_id from fct_seller_orders where order_month < date '2017-01-01')"""
data = {
  "late_by_month": [{"m": m, "late": l, "n": n} for m, l, n in q("""
      select strftime(order_month,'%Y-%m'), sum(is_late::int), count(is_late)
      from fct_orders where in_window group by 1 order by 1""")],
  "review_by_lateness": [{"b": b[2:], "avg": a, "n": n, "low": lo} for b, a, n, lo in q("""
      with d as (select f.review_score, date_diff('day', o.estimated_delivery_date, o.delivered_at::date) dl
                 from fct_orders f join stg_orders o using (order_id)
                 where f.in_window and f.has_review and o.delivered_at is not null)
      select case when dl <= 0 then '0 On time' when dl <= 3 then '1 1-3 days late' when dl <= 7 then '2 4-7 days late'
                  when dl <= 14 then '3 8-14 days late' else '4 15+ days late' end,
             avg(review_score), count(*), avg((review_score <= 2)::int)
      from d group by 1 order by 1""")],
  "retention": [{"k": k, "active": a, "n": n} for k, a, n in q(f"""
      select months_since_first, sum(is_active::int), count(*) from fct_seller_months
      where {new_sellers} and months_since_first between 1 and 12 group by 1 order by 1""")],
  "segments": [{"s": s, "n": n, "back": b, "avg": a, "med": m} for s, n, b, a, m in q(f"""
      with s6 as (
        select seller_id, min(cohort_month) cm,
               sum(orders) filter (where months_since_first = 0) m0,
               coalesce(sum(item_value) filter (where months_since_first between 1 and 6), 0) v6,
               max((months_since_first between 1 and 6 and is_active)::int) back
        from fct_seller_months where {new_sellers} group by 1 having min(cohort_month) <= date '2018-02-01')
      select case when m0 = 1 then '1 order' when m0 <= 4 then '2-4 orders' else '5+ orders' end,
             count(*), avg(back), avg(v6), quantile_cont(v6, 0.5)
      from s6 group by 1 order by 1""")],
}
k = q("""select sum(is_failed::int), count(*), sum(is_late::int), count(is_late) from fct_orders where in_window""")[0]
v = q("""select sum(item_value) filter (where active_months >= 7), sum(item_value), count(*) filter (where active_months >= 7) from dim_sellers where orders > 0""")[0]
b3 = q(f"""with s as (select seller_id, min(cohort_month) cm, max((months_since_first between 1 and 3 and is_active)::int) b
            from fct_seller_months where {new_sellers} group by 1)
            select sum(b), count(*) from s where cm <= date '2018-05-01'""")[0]
data["kpis"] = {"back3": b3[0], "cohort3": b3[1], "failed": k[0], "orders": k[1], "late": k[2], "delivered": k[3], "v7": v[0], "vall": v[1], "s7": v[2]}

# extra tables for the report
data["outcomes"] = q("""select count(*), sum(is_failed::int), sum(is_delivered::int), count(is_late), sum(is_late::int) from fct_orders where in_window""")[0]
data["promise"] = [{"m": m, "promised": p, "actual": a} for m, p, a in q("""
    select strftime(f.order_month,'%Y-%m'), avg(date_diff('day', o.purchased_at::date, o.estimated_delivery_date)), avg(f.days_to_deliver)
    from fct_orders f join stg_orders o using (order_id)
    where f.in_window and f.is_late is not null and f.order_month between '2017-10-01' and '2018-06-01' group by 1 order by 1""")]
data["seller_late"] = q("""
    with s as (select seller_id, count(*) n, sum(is_late::int) late from fct_seller_orders
               where in_window and is_late is not null group by 1 having count(*) >= 30)
    select count(*), sum(n), sum(late), quantile_cont(late*1.0/n, 0.5), quantile_cont(late*1.0/n, 0.9),
           sum((late*1.0/n >= 0.15)::int), sum(late) filter (where late*1.0/n >= 0.15) from s""")[0]
fm = f"""
    with sm as (select * from fct_seller_months where {new_sellers}),
    s as (select seller_id, min(cohort_month) cm, max((months_since_first between 1 and 3 and is_active)::int) back
          from sm group by 1 having min(cohort_month) <= date '2018-05-01'),
    f as (select so.seller_id, count(*) n0, max(coalesce(so.is_late,false)::int) any_late, avg(so.review_score) rv
          from fct_seller_orders so join (select distinct seller_id, cohort_month from sm) c
            on c.seller_id = so.seller_id and so.order_month = c.cohort_month
          where so.in_window group by 1)
    select case when f.n0 = 1 then '1 order' when f.n0 <= 4 then '2-4 orders' else '5+ orders' end size, GROUPCOL grp,
           count(*), sum(s.back) from s join f using (seller_id) WHERECLAUSE group by 1, 2 order by 1, 2"""
data["first_late"] = q(fm.replace("GROUPCOL", "case when f.any_late = 1 then 'Some late' else 'None late' end").replace("WHERECLAUSE", ""))
data["first_review"] = q(fm.replace("GROUPCOL", "case when f.rv <= 2 then 'Avg 2 or below' else 'Avg above 2' end").replace("WHERECLAUSE", "where f.rv is not null"))
data["tenure_value"] = q("""
    select case when active_months = 1 then '1 month' when active_months <= 3 then '2 to 3 months'
                when active_months <= 6 then '4 to 6 months' else '7+ months' end, count(*), sum(item_value)
    from dim_sellers where orders > 0 group by 1 order by 1""")
data["starters_2017"] = q(f"""
    with sm as (select * from fct_seller_months where {new_sellers})
    select count(*) from (select seller_id, min(cohort_month) cm, sum(orders) filter (where months_since_first = 0) m0
                          from sm group by 1) where m0 = 1 and year(cm) = 2017""")[0][0]
data["sales_2017"] = q("select sum(item_value) from fct_seller_orders where year(order_month) = 2017")[0][0]
data["counts"] = {"orders_all": q("select count(*) from fct_orders")[0][0], "sellers": q("select count(*) from dim_sellers")[0][0],
                  "multi_seller": q("select count(*) from fct_orders where seller_count > 1")[0][0]}

html = (ROOT / "scripts" / "report_template.html").read_text().replace("__DATA__", json.dumps(data, default=float))
(ROOT / "docs" / "index.html").write_text(html)
print("wrote docs/index.html")
