-- One row = one seller in one calendar month, from the seller's first month in the window
-- through the end of the window, including months with no orders. This is the retention base.
with activity as (
    select seller_id, order_month, count(*) as orders, sum(item_value) as item_value
    from {{ ref('fct_seller_orders') }}
    where in_window
    group by 1, 2
),
first_month as (
    select seller_id, min(order_month) as cohort_month from activity group by 1
),
months as (
    select unnest(generate_series(date '{{ var("window_start") }}', date '{{ var("window_end") }}', interval 1 month))::date as month
)
select
    f.seller_id,
    f.cohort_month,
    m.month,
    date_diff('month', f.cohort_month, m.month)  as months_since_first,
    coalesce(a.orders, 0)                        as orders,
    coalesce(a.item_value, 0)                    as item_value,
    a.orders is not null                         as is_active
from first_month f
join months m on m.month >= f.cohort_month
left join activity a on a.seller_id = f.seller_id and a.order_month = m.month
