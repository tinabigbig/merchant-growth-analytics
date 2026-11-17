# Question 3: Which new-seller segment has the biggest opportunity, and what is it worth?
# Reads the dbt marts. New seller = no order before Jan 2017.
# Value = item value (price, excl. freight). Olist's commission is not in the data, so this is sales, not revenue.
import duckdb
c = duckdb.connect("data/olist.duckdb", read_only=True)
def q(sql): return c.execute(sql).fetchall()

# One row = one new seller, with first-month size and value in the 6 months after the first month.
# Cohorts Jan 2017 to Feb 2018, so every seller has 6 full months of follow-up.
c.execute("""
create temp view seller_6m as
with new_months as (
    select * from fct_seller_months
    where seller_id not in (select seller_id from fct_seller_orders where order_month < date '2017-01-01'))
select seller_id,
       min(cohort_month)                                                   as cohort_month,
       sum(orders) filter (where months_since_first = 0)                   as first_month_orders,
       sum(item_value) filter (where months_since_first = 0)               as first_month_value,
       coalesce(sum(item_value) filter (where months_since_first between 1 and 6), 0) as value_next_6m,
       max((months_since_first between 1 and 6 and is_active)::int)        as active_next_6m
from new_months group by 1
having min(cohort_month) <= date '2018-02-01'
""")
seg = "case when first_month_orders = 1 then '1 order' when first_month_orders <= 4 then '2-4 orders' else '5+ orders' end"

# 1. Segment table
print("1. New sellers by first-month size (cohorts Jan 2017 to Feb 2018)")
rows = q(f"""
    select {seg} s, count(*) n, round(100*count(*)/sum(count(*)) over (),1) pct,
           round(100*avg(active_next_6m),1) active_pct,
           round(avg(value_next_6m)) avg_6m, round(quantile_cont(value_next_6m,0.5)) med_6m,
           round(sum(value_next_6m)) total_6m
    from seller_6m group by 1 order by 1""")
for r in rows:
    print("   {:10s} sellers {:>5,} ({:>4}%) | sold again in 6 months {:>4}% | value next 6 months: avg {:>7,.0f}, median {:>6,.0f}, total {:>10,.0f}".format(*r))
v = {r[0]: r[4] for r in rows}
n1 = {r[0]: r[1] for r in rows}["1 order"]

# 2. How many one-order starters arrive per year? Full year 2017.
per_year = q(f"select count(*) from seller_6m where {seg} = '1 order' and year(cohort_month) = 2017")[0][0]
print(f"\n2. New one-order starters in 2017: {per_year:,}")

# 3. Sizing. If a share of one-order starters performed like 2-4 order starters,
#    the extra 6-month sales per moved seller is the gap in averages. The gap is an association,
#    so only part of it is assumed to be caused by first-month size (incremental share).
gap = v["2-4 orders"] - v["1 order"]
print(f"\n3. Gap in average 6-month sales, 2-4 order vs 1-order starters: {gap:,.0f}")
print("   Opportunity per year = starters x share moved x gap x incremental share")
for name, moved, incr in [("low", 0.05, 0.25), ("base", 0.10, 0.50), ("high", 0.20, 0.75)]:
    value = per_year * moved * gap * incr
    print(f"   {name:5s} move {moved:.0%}, {incr:.0%} of gap is real: {per_year:,} x {moved:.0%} x {gap:,.0f} x {incr:.0%} = {value:,.0f}")

# 4. Scale check: total marketplace item value in 2017
total_2017 = q("select sum(item_value) from fct_seller_orders where year(order_month) = 2017")[0][0]
print(f"\n4. For scale: all item value in 2017 = {total_2017:,.0f}")
