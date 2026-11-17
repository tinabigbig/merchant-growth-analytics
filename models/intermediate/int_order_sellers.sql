-- One row = one seller's part of one order (order_id, seller_id).
-- 1,278 orders include items from 2+ sellers, so seller metrics are built on this grain.
select
    order_id,
    seller_id,
    count(*)           as units,
    sum(price)         as item_value,
    sum(freight_value) as freight_value
from {{ ref('stg_order_items') }}
group by 1, 2
