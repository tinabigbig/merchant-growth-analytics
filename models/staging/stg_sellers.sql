-- One row = one seller (the marketplace's merchants).
select seller_id, seller_city, seller_state
from read_csv_auto('{{ var("raw_path") }}/olist_sellers_dataset.csv', header = true)
