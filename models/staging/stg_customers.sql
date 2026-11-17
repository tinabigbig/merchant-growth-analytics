-- One row = one customer_id. Olist issues a new customer_id on every order;
-- customer_unique_id is the person, so repeat purchase is counted on customer_unique_id.
select
    customer_id,
    customer_unique_id,
    customer_state
from read_csv_auto('{{ var("raw_path") }}/olist_customers_dataset.csv', header = true)
