# Step 1: grain and joins

Source: Olist Brazilian E-Commerce Public Dataset (Kaggle), orders placed Sep 2016 to Oct 2018.
Run: `python -I scripts/step1_grain_and_joins.py`

## One row in each table

| Table | One row is | Key unique? |
|---|---|---|
| orders | one order | yes, 99,441 |
| customers | one customer_id, which is issued per order | yes, 99,441 |
| order_items | one unit on an order (order_id, order_item_id) | yes, 112,650 |
| payments | one payment on an order (order_id, payment_sequential) | yes, 103,886 |
| reviews | not one row per order: 547 orders have 2+ reviews, and 789 review_ids sit on 2+ orders | no |
| products | one product | yes, 32,951 |
| sellers | one seller | yes, 3,095 |

## What this means for the build

1. **People are customer_unique_id, not customer_id.** customer_id is new on every order. 99,441 customer_ids belong to 96,096 people. Counting repeat purchase on customer_id would show zero repeats.
2. **Reviews need a rule before any review metric.** Keep one review per order: the most recent answer.
3. **Merchant metrics need an order-seller grain.** 1,278 orders contain items from 2+ sellers, so "orders per seller" must count (order_id, seller_id) pairs.
4. **775 orders have no items.** 603 are unavailable and 164 canceled. They count in order-experience metrics (orders that never shipped) but carry no value.
5. **The edges are thin.** Sep to Dec 2016 has about 330 orders, and Sep to Oct 2018 has 20. Monthly trends and cohorts use Jan 2017 to Aug 2018.
6. **Item value and payments differ by about 165,000 (1%).** Payments include instalment interest. Merchant revenue uses item price; freight is reported separately.
7. **8 delivered orders have no delivery date.** They are excluded from delivery-time metrics only.

## A finding that changes the questions

Only 3.0% of people with a delivered order bought twice (2,801 of 93,358). Customer repeat purchase is too thin to carry a retention analysis on its own.

The sellers are the better unit. They are this marketplace's merchants, like Owner's restaurants: 3,095 sellers, median 6 orders each, 1,271 with 10 or more orders, and sellers with 100+ orders bring in 51.5% of item value. Retention is studied as **merchant retention**: does a seller keep selling month after month, and what separates the ones who grow from the ones who stop?
