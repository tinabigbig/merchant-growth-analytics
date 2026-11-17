-- One row = one product, with the English category name.
select
    p.product_id,
    coalesce(t.product_category_name_english, p.product_category_name, 'unknown') as category
from read_csv_auto('{{ var("raw_path") }}/olist_products_dataset.csv', header = true) p
left join read_csv_auto('{{ var("raw_path") }}/product_category_name_translation.csv', header = true) t
    using (product_category_name)
