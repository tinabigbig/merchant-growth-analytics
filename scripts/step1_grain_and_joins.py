# Step 1: What is one row in each table, and do the tables join cleanly?
# Nothing is cleaned here. This step only looks and counts.
import duckdb
from pathlib import Path

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
con = duckdb.connect()
tables = {
    "orders": "olist_orders_dataset.csv", "customers": "olist_customers_dataset.csv",
    "items": "olist_order_items_dataset.csv", "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv", "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
}
for name, f in tables.items():
    con.execute(f"create view {name} as select * from read_csv_auto('{RAW / f}', header=true)")

def q(sql):
    return con.execute(sql).fetchall()

def one(sql):
    return q(sql)[0][0]

# 1. Grain: rows versus distinct candidate keys
print("Grain check (rows vs distinct key):")
for name, key in [("orders", "order_id"), ("customers", "customer_id"), ("items", "order_id, order_item_id"),
                  ("payments", "order_id, payment_sequential"), ("reviews", "review_id"),
                  ("reviews", "order_id"), ("products", "product_id"), ("sellers", "seller_id")]:
    rows = one(f"select count(*) from {name}")
    distinct = one(f"select count(*) from (select distinct {key} from {name})")
    print(f"  {name:10s} key ({key}): rows {rows:,}  distinct {distinct:,}  {'OK' if rows == distinct else 'NOT UNIQUE'}")
print()

# 2. People: customer_id is issued per order; customer_unique_id is the person
print(f"customer_id values: {one('select count(distinct customer_id) from customers'):,}")
print(f"customer_unique_id values (people): {one('select count(distinct customer_unique_id) from customers'):,}")
print()

# 3. Reviews: how many orders have more than one review, and how many review_ids sit on more than one order
print(f"Orders with 2+ reviews: {one('select count(*) from (select order_id from reviews group by 1 having count(*) > 1)'):,}")
print(f"review_ids on 2+ orders: {one('select count(*) from (select review_id from reviews group by 1 having count(distinct order_id) > 1)'):,}")
print()

# 4. Joins: orphans in each direction
checks = {
    "orders without a customer": "select count(*) from orders o left join customers c using (customer_id) where c.customer_id is null",
    "orders without items": "select count(*) from orders o where not exists (select 1 from items i where i.order_id = o.order_id)",
    "items without an order": "select count(*) from items i where not exists (select 1 from orders o where o.order_id = i.order_id)",
    "items without a seller": "select count(*) from items i where not exists (select 1 from sellers s where s.seller_id = i.seller_id)",
    "items without a product": "select count(*) from items i where not exists (select 1 from products p where p.product_id = i.product_id)",
    "orders without payments": "select count(*) from orders o where not exists (select 1 from payments p where p.order_id = o.order_id)",
    "orders without a review": "select count(*) from orders o where not exists (select 1 from reviews r where r.order_id = o.order_id)",
    "orders with 2+ sellers": "select count(*) from (select order_id from items group by 1 having count(distinct seller_id) > 1)",
}
print("Join checks:")
for label, sql in checks.items():
    print(f"  {label:28s} {one(sql):,}")
print()

# 5. Order status and dates
print("Order status:")
for s, n in q("select order_status, count(*) from orders group by 1 order by 2 desc"):
    print(f"  {s:12s} {n:,}")
print("Purchase date range:", q("select min(order_purchase_timestamp), max(order_purchase_timestamp) from orders")[0])
print("Orders per month (first and last 4):")
months = q("select strftime(order_purchase_timestamp, '%Y-%m') m, count(*) from orders group by 1 order by 1")
for m, n in months[:4] + [("...", "")] + months[-4:]:
    print(f"  {m} {n}")
print()

# 6. Delivered orders missing a delivery date, and items vs payments value
no_date = one("select count(*) from orders where order_status = 'delivered' and order_delivered_customer_date is null")
print(f"Delivered but no delivered-to-customer date: {no_date:,}")
item_total = one("select sum(price + freight_value) from items")
pay_total = one("select sum(payment_value) from payments")
print(f"Item price + freight total: {item_total:,.2f}   Payments total: {pay_total:,.2f}   gap {pay_total - item_total:,.2f}")
