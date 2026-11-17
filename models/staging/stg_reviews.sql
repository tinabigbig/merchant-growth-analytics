-- One row = one review record as delivered. NOT one per order:
-- some orders have 2+ reviews and some review_ids sit on 2+ orders. int_order_reviews fixes that.
select
    review_id,
    order_id,
    cast(review_score as integer)            as review_score,
    cast(review_creation_date as timestamp)  as review_created_at,
    cast(review_answer_timestamp as timestamp) as review_answered_at
from read_csv_auto('{{ var("raw_path") }}/olist_order_reviews_dataset.csv', header = true)
