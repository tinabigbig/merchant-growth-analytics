-- One row = one order that has a review.
-- Rule: when an order has 2+ reviews, keep the most recent answer.
select order_id, review_id, review_score, review_answered_at
from {{ ref('stg_reviews') }}
qualify row_number() over (
    partition by order_id
    order by review_answered_at desc, review_created_at desc, review_id
) = 1
