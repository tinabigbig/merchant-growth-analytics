-- Fails if any seller has two rows for the same month.
select seller_id, month, count(*) as n
from {{ ref('fct_seller_months') }}
group by 1, 2
having count(*) > 1
