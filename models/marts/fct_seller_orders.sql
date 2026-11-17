-- One row = one seller's part of one order, with that order's experience measures.
-- Review score and lateness belong to the whole order; on multi-seller orders each seller carries them.
select
    os.order_id,
    os.seller_id,
    o.order_month,
    o.in_window,
    o.customer_unique_id,
    os.units,
    os.item_value,
    os.freight_value,
    o.is_delivered,
    o.is_late,
    o.days_to_deliver,
    o.review_score,
    o.seller_count > 1 as is_multi_seller_order
from {{ ref('int_order_sellers') }} os
join {{ ref('fct_orders') }} o using (order_id)
