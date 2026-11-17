-- One row = one seller, with lifetime measures inside the analysis window.
with so as (select * from {{ ref('fct_seller_orders') }} where in_window)
select
    s.seller_id,
    s.seller_state,
    min(so.order_month)                                   as first_month,
    max(so.order_month)                                   as last_month,
    count(distinct so.order_month)                        as active_months,
    count(so.order_id)                                    as orders,
    coalesce(sum(so.item_value), 0)                       as item_value,
    avg(so.is_late::int) filter (where so.is_late is not null)      as late_rate,
    avg(so.review_score)                                  as avg_review_score,
    count(distinct so.customer_unique_id)                 as customers
from {{ ref('stg_sellers') }} s
left join so using (seller_id)
group by 1, 2
