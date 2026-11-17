# Question 2: merchant retention

Run: `python -I scripts/q2_merchant_retention.py` after `dbt build`. Window: Jan 2017 to Aug 2018.

## Answer

About a quarter of new sellers never sell again within three months, and the strongest early sign is how big the first month was. A bad first month of reviews goes with much lower return; a late first delivery barely moves it. Long-lived sellers carry the business: those active 7+ months bring in 80% of item value.

| Number | One row is | Filter | Numerator / denominator |
|---|---|---|---|
| 57.6% active in month 1, 52.4% in month 3, 44.4% in month 6, 35.2% in month 12 | a new seller | cohort has k months of follow-up | e.g. month 3: 1,266 / 2,414 |
| 75.9% sold again within months 1 to 3 | a new seller | cohorts Jan 2017 to May 2018 | 1,832 / 2,414 |
| Came back: 66.5% after a 1-order first month, 87.4% after 2 to 4, 98.0% after 5+ | same | no late first-month delivery | 882 / 1,326; 595 / 681; 149 / 152 |
| Late first delivery vs none: 61.4% vs 66.5% (1 order), 87.0% vs 87.4% (2 to 4) | same | within first-month size | 54 / 88 vs 882 / 1,326; 80 / 92 vs 595 / 681 |
| First-month avg review 2 or below vs above 2: 51.4% vs 69.5% (1 order), 46.9% vs 90.1% (2 to 4) | same | within first-month size | 130 / 253 vs 799 / 1,150; 23 / 49 vs 652 / 724 |
| Sellers active 7+ months hold 80.4% of item value | a seller | any order in window | 884 of 3,068 sellers |

New seller = no order before Jan 2017. 145 sellers that sold in 2016 are excluded from the cohort figures, since their first month in the window is not their real first month.

## What stands out

1. **Retention is a curve that keeps falling.** Just over half of new sellers are active in a given month 3 months in; about a third at 12 months. The rate is steady across cohorts (74% to 78% come back within 3 months), so this is how the marketplace works, not a bad quarter.
2. **First-month size is the strongest early signal.** One-order starters come back two times in three. Sellers with 5+ first-month orders almost always do.
3. **Bad first reviews matter more than late first deliveries.** Comparing sellers of the same first-month size, a late delivery moves return by 0 to 5 points. A first-month average review of 2 or below cuts it by 18 points for one-order starters and 43 points for 2 to 4 order starters.
4. **The value sits in the survivors.** 884 sellers active 7+ months carry 80% of item value; 738 one-month sellers carry under 2%.

## Product reading

The highest-value onboarding goal is getting a new seller from one order to several in their first month, and protecting their first reviews: flag new sellers early, check their first orders, and step in when the first review is low. For Owner, the same question applies to restaurants in their first 30 days.

## Limits

- Active means at least one order in that month. A seller with no orders may still be listed.
- The first-month comparisons are associations. Sellers who start small or get bad reviews may differ in product, price or effort, so this ranks where to look, not what causes churn.
- Groups with fewer than 50 sellers (5+ orders with a low first review: 6 sellers) are too small to read.
- Review score belongs to the whole order; on multi-seller orders each seller carries it.
