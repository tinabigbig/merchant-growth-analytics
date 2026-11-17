-- One row = one unit on an order (order_id, order_item_id).
select
    order_id,
    order_item_id,
    product_id,
    seller_id,
    cast(price as double)         as price,
    cast(freight_value as double) as freight_value
from read_csv_auto('{{ var("raw_path") }}/olist_order_items_dataset.csv', header = true)
