-- Fails if any (order_id, seller_id) pair appears more than once.
select order_id, seller_id, count(*) as n
from {{ ref('int_order_sellers') }}
group by 1, 2
having count(*) > 1
