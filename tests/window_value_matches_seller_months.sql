-- Fails if seller-month value in the window differs from seller-order value in the window.
with a as (select sum(item_value) v from {{ ref('fct_seller_orders') }} where in_window),
     b as (select sum(item_value) v from {{ ref('fct_seller_months') }})
select * from a, b where abs(a.v - b.v) > 0.01
