-- Fails if item value is lost or double-counted between the raw items and each mart.
with raw as (select sum(price) v from {{ ref('stg_order_items') }}),
     orders as (select sum(item_value) v from {{ ref('fct_orders') }}),
     seller_orders as (select sum(item_value) v from {{ ref('fct_seller_orders') }})
select * from raw, orders, seller_orders
where abs(raw.v - orders.v) > 0.01 or abs(raw.v - seller_orders.v) > 0.01
