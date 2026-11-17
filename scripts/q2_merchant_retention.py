# Question 2: Do new sellers keep selling, and do sellers whose first orders arrived late stop sooner?
# Reads the dbt marts. One row in fct_seller_months = one seller in one month, from their first month on.
import duckdb
c = duckdb.connect("data/olist.duckdb", read_only=True)
def q(sql): return c.execute(sql).fetchall()
LAST = "2018-08-01"   # last month in the window

# New sellers only: 145 sellers already sold before Jan 2017, so their first month in the window is not their first month.
c.execute("""create temp view new_seller_months as
    select * from fct_seller_months
    where seller_id not in (select seller_id from fct_seller_orders where order_month < date '2017-01-01')""")

# 1. Retention curve. A seller counts at month k only if their cohort has k months of follow-up,
#    so recent cohorts are not counted as "lost" just because time ran out.
print("1. Share of new sellers active in month k after their first month (all cohorts with k months of data)")
for k, n, active, pct in q(f"""
    select months_since_first k, count(*) n, sum(is_active::int), round(100*avg(is_active::int),1)
    from new_seller_months
    where months_since_first in (1, 2, 3, 6, 12)
    group by 1 order by 1"""):
    print(f"   month {k:>2}: {active:>5,} active / {n:>5,} sellers  = {pct}%")

# 2. Ever came back: active in any of months 1 to 3. Cohorts up to May 2018 (3 months of data).
print("\n2. Active again in months 1 to 3, by cohort quarter (cohorts Jan 2017 to May 2018)")
base = f"""
    with s as (
      select seller_id, min(cohort_month) cohort_month,
             max((months_since_first between 1 and 3 and is_active)::int) back_1_3
      from new_seller_months group by 1)
    select * from s where cohort_month <= date '{LAST}' - interval 3 month"""
for qtr, n, back, pct in q(f"""
    select strftime(cohort_month,'%Y') || '-Q' || quarter(cohort_month), count(*), sum(back_1_3), round(100*avg(back_1_3),1)
    from ({base}) group by 1 order by 1"""):
    print(f"   {qtr}: {back:>4,} / {n:>4,} = {pct}%")
total = q(f"select count(*), sum(back_1_3), round(100*avg(back_1_3),1) from ({base})")[0]
print(f"   all:     {total[1]:>4,} / {total[0]:>4,} = {total[2]}%")

# 3. First-month experience vs coming back. First month = the seller's cohort month.
#    Busier sellers have more chances to be late AND more reason to stay, so compare within first-month size.
print("\n3. Came back in months 1 to 3: first-month orders with any late delivery vs none, within first-month size")
for size, grp, n, back, pct in q(f"""
    with first_month as (
      select so.seller_id, count(*) orders_m0,
             max(coalesce(so.is_late, false)::int) any_late,
             avg(so.review_score) avg_review
      from fct_seller_orders so
      join (select distinct seller_id, cohort_month from new_seller_months) sm
        on sm.seller_id = so.seller_id and so.order_month = sm.cohort_month
      where so.in_window group by 1),
    s as ({base})
    select case when f.orders_m0 = 1 then '1 order' when f.orders_m0 <= 4 then '2-4 orders' else '5+ orders' end size,
           case when f.any_late = 1 then 'some late' else 'none late' end grp,
           count(*), sum(s.back_1_3), round(100*avg(s.back_1_3),1)
    from s join first_month f using (seller_id)
    group by 1, 2 order by 1, 2"""):
    print(f"   {size:10s} {grp:9s} {back:>4,} / {n:>4,} = {pct}%")

# 4. Same idea with first-month reviews: avg review 2 or below vs above 2.
print("\n4. Came back in months 1 to 3: first-month average review <= 2 vs > 2, within first-month size")
for size, grp, n, back, pct in q(f"""
    with first_month as (
      select so.seller_id, count(*) orders_m0, avg(so.review_score) avg_review
      from fct_seller_orders so
      join (select distinct seller_id, cohort_month from new_seller_months) sm
        on sm.seller_id = so.seller_id and so.order_month = sm.cohort_month
      where so.in_window group by 1),
    s as ({base})
    select case when f.orders_m0 = 1 then '1 order' when f.orders_m0 <= 4 then '2-4 orders' else '5+ orders' end,
           case when f.avg_review <= 2 then 'avg <= 2' else 'avg > 2' end,
           count(*), sum(s.back_1_3), round(100*avg(s.back_1_3),1)
    from s join first_month f using (seller_id)
    where f.avg_review is not null
    group by 1, 2 order by 1, 2"""):
    print(f"   {size:10s} {grp:9s} {back:>4,} / {n:>4,} = {pct}%")

# 5. Where the value sits: sellers by months active in the window.
print("\n5. Item value by how many months a seller was active")
for b, n, val, pct in q("""
    select case when active_months = 1 then '1 month' when active_months <= 3 then '2-3 months'
                when active_months <= 6 then '4-6 months' else '7+ months' end b,
           count(*), round(sum(item_value)), round(100*sum(item_value)/sum(sum(item_value)) over (),1)
    from dim_sellers where orders > 0 group by 1 order by 1"""):
    print(f"   {b:10s} sellers {n:>5,} | item value {val:>12,.0f} | {pct}% of value")
