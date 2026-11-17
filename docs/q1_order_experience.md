# Question 1: order experience

Run: `python -I scripts/q1_order_experience.py` after `dbt build`. Window: orders placed Jan 2017 to Aug 2018.

## Answer

Few orders fail, but late delivery is the experience problem, and it is driven by time, not by a few bad sellers. Late orders are reviewed far worse, and the damage grows with every day late.

| Number | One row is | Filter | Numerator / denominator |
|---|---|---|---|
| 1.19% of orders failed | an order | placed in window | 1,182 canceled or unavailable / 99,092 orders |
| 6.79% of delivered orders were late | an order | delivered with a delivery date | 6,532 delivered after the estimated date / 96,204 |
| Late reviews avg 2.27 vs 4.29 on time | an order | delivered with a date and a review | 6,379 late, 89,182 on time |
| 62.4% of late orders got 1 to 2 stars vs 9.2% on time | same | same | share of each group |
| Seller late rates: median 5.5%, 90th percentile 12.6% | a seller | 30+ delivered orders with a date | 625 sellers |
| Sellers at 15%+ late hold 9.4% of late orders | same | same | 516 / 5,483 late orders |

## What stands out

1. **Lateness spikes by month.** Normal months run 3 to 5% late. November 2017 hit 12.4% (the Black Friday month), February 2018 14.1% and March 2018 19.0%.
2. **In early 2018 the promise got shorter while delivery got slower.** March 2018 orders were promised 22.7 days on average, the shortest of the period, while actual delivery took 16.2 days, the slowest. The estimate did not adjust to what the network could do.
3. **Reviews fall with each day late.** On time 4.29. 1 to 3 days late 3.29. 4 to 7 days 2.10. 8+ days about 1.7, with about 80% of those orders at 1 to 2 stars.
4. **It is not a few bad sellers.** The 37 sellers above 15% late hold under a tenth of late orders. Most late orders come from ordinary sellers in bad months.

## Product reading

The lever is the delivery promise and peak capacity, not policing sellers: set delivery estimates from current delivery times, widen them in peak months, and warn customers early when an order will miss. Seller-level enforcement would reach under 10% of late orders.

## Limits

- Late is measured against the estimate shown to the customer, not against a service standard.
- The review gap is an association. Late orders may also differ in product, region or price. The strong step-down by days late makes it likely, not proven, that lateness itself lowers scores.
- Review score and lateness belong to the whole order; on the 1,278 multi-seller orders every seller carries them.
