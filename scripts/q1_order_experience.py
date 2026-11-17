# Question 1: How many orders fail or arrive late, and are late orders reviewed worse?
# Reads the dbt marts. Window: orders placed Jan 2017 to Aug 2018.
import duckdb
c = duckdb.connect("data/olist.duckdb", read_only=True)
def q(sql): return c.execute(sql).fetchall()

# 1. Outcome of every order. One row = one order in the window.
print("1. Order outcomes (one row = one order placed in the window)")
for r in q("""
    select count(*) orders,
           sum(is_failed::int) failed, round(100*avg(is_failed::int),2) failed_pct,
           sum(is_delivered::int) delivered,
           count(is_late) delivered_with_date,
           sum(is_late::int) late, round(100*avg(is_late::int),2) late_pct
    from fct_orders where in_window"""):
    print("   orders {:,} | failed {:,} ({}%) | delivered {:,} | with delivery date {:,} | late {:,} ({}% of those with a date)".format(*r))

# 2. Late rate by month. Denominator = delivered orders with a delivery date.
print("\n2. Late rate by order month (late / delivered with a date)")
for m, n, late, pct in q("""
    select strftime(order_month,'%Y-%m'), count(is_late), sum(is_late::int), round(100*avg(is_late::int),1)
    from fct_orders where in_window group by 1 order by 1"""):
    print(f"   {m}  {late:>5,} / {n:>5,}  {pct:>5}%  " + "#" * int(pct))

# 3. Review score: late vs on time. One row = delivered order with a date and a review.
print("\n3. Reviews: late vs on time (delivered orders with a date and a review)")
for r in q("""
    select case when is_late then 'late' else 'on time' end grp, count(*) n,
           round(avg(review_score),2) avg_score,
           round(100*avg((review_score<=2)::int),1) one_two_star_pct,
           round(100*avg((review_score=5)::int),1) five_star_pct
    from fct_orders where in_window and is_late is not null and has_review group by 1 order by 1"""):
    print("   {:8s} n {:>6,} | avg {} | 1-2 stars {}% | 5 stars {}%".format(*r))

# 4. Does it get worse with how late? Days late = delivered date minus estimated date.
print("\n4. Review score by days late")
for r in q("""
    with d as (
      select f.review_score, date_diff('day', o.estimated_delivery_date, o.delivered_at::date) days_late
      from fct_orders f join stg_orders o using (order_id)
      where f.in_window and f.has_review and o.delivered_at is not null)
    select case when days_late <= 0 then '0 on time'
                when days_late <= 3 then '1 1-3 days'
                when days_late <= 7 then '2 4-7 days'
                when days_late <= 14 then '3 8-14 days'
                else '4 15+ days' end b,
           count(*), round(avg(review_score),2), round(100*avg((review_score<=2)::int),1)
    from d group by 1 order by 1"""):
    print("   {:12s} n {:>6,} | avg {} | 1-2 stars {}%".format(r[0][2:], *r[1:]))

# 5. Is lateness concentrated in a few sellers? One row = seller with 30+ delivered orders with a date.
print("\n5. Seller concentration of late orders (sellers with 30+ delivered orders with a date)")
r = q("""
    with s as (select seller_id, count(*) n, sum(is_late::int) late
               from fct_seller_orders where in_window and is_late is not null group by 1 having count(*) >= 30)
    select count(*), sum(n), sum(late), quantile_cont(late*1.0/n, 0.5), quantile_cont(late*1.0/n, 0.9),
           sum((late*1.0/n >= 0.15)::int), sum(late) filter (where late*1.0/n >= 0.15)
    from s""")[0]
print(f"   sellers {r[0]:,} | their delivered orders {r[1]:,} | late {r[2]:,}")
print(f"   median seller late rate {100*r[3]:.1f}% | 90th percentile {100*r[4]:.1f}%")
print(f"   sellers at 15%+ late: {r[5]:,} of {r[0]:,} ({100*r[5]/r[0]:.1f}%), carrying {r[6]:,} of {r[2]:,} late orders ({100*r[6]/r[2]:.1f}%)")
