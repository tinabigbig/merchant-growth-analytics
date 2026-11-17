-- One row = one order, with the order-experience measures.
with items as (
    select order_id, sum(item_value) as item_value, sum(freight_value) as freight_value,
           count(*) as seller_count
    from {{ ref('int_order_sellers') }}
    group by 1
)
select
    o.order_id,
    c.customer_unique_id,
    o.order_status,
    o.purchased_at,
    date_trunc('month', o.purchased_at)::date                        as order_month,
    o.purchased_at::date between '{{ var("window_start") }}' and '{{ var("window_end") }}' as in_window,
    coalesce(i.item_value, 0)                                        as item_value,
    coalesce(i.freight_value, 0)                                     as freight_value,
    coalesce(i.seller_count, 0)                                      as seller_count,
    o.order_status = 'delivered'                                     as is_delivered,
    o.order_status in ('canceled', 'unavailable')                    as is_failed,
    -- delivery measures only where a delivery date exists (8 delivered orders have none)
    case when o.delivered_at is not null
         then date_diff('day', o.purchased_at, o.delivered_at) end    as days_to_deliver,
    case when o.delivered_at is not null
         then o.delivered_at::date > o.estimated_delivery_date end   as is_late,
    r.review_score,
    r.review_id is not null                                          as has_review
from {{ ref('stg_orders') }} o
join {{ ref('stg_customers') }} c using (customer_id)
left join items i using (order_id)
left join {{ ref('int_order_reviews') }} r using (order_id)
