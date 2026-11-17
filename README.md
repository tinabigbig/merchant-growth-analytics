# Merchant Growth & Retention Analytics

Independent case study on the public Olist Brazilian e-commerce dataset: about 99,000 marketplace orders from 3,095 independent sellers, Sep 2016 to Oct 2018. Built with dbt, SQL and Python.

The sellers here play the role restaurants play on a platform like Owner: small merchants trying to grow online sales. The case study asks three product questions and answers each with tested models and an independent check.

## Questions and answers

| Question | Answer |
|---|---|
| 1. Order experience: where does it break? | 1.19% of orders fail, but 6.79% of delivered orders arrive late. Late orders average 2.27 stars vs 4.29 on time. Lateness spikes in peak months (19.0% in March 2018) and is not concentrated in a few sellers. |
| 2. Merchant retention: who keeps selling? | 75.9% of new sellers sell again within 3 months. A one-order first month and a bad first review go with much lower return; a late first delivery barely does. Sellers active 7+ months carry 80.4% of sales. |
| 3. Segments and sizing: where is the opportunity? | 59% of new sellers start with one order. Moving some of them up is worth about R$63,000 a year in the base case (low R$16,000, high R$188,000), roughly 1% of sales: enough for automated help, not a staffed program. |

**Read the full report:** [tinabigbig.github.io/merchant-growth-analytics](https://tinabigbig.github.io/merchant-growth-analytics/) (source: `docs/index.html`). A one-page summary is in the [product memo](docs/product_memo.md).

## How it is built

```
data/raw/                CSVs from Kaggle (not committed)
models/staging/          raw tables with types fixed
models/intermediate/     one review per order; one row per seller per order
models/marts/            fct_orders, fct_seller_orders, fct_seller_months, dim_sellers
tests/                   uniqueness and reconciliation tests
scripts/                 step 1 checks, one script per question, report builder
checks/                  independent pandas check of every headline number
docs/                    findings per step, product memo, report (index.html)
```

Rules set in step 1 before anything was counted ([step 1 findings](docs/step1_findings.md)):

- A customer is `customer_unique_id`; `customer_id` is new on every order.
- Reviews are not one per order. Keep the most recent answer.
- 1,278 orders have items from 2+ sellers, so seller metrics use one row per seller per order.
- Analysis window Jan 2017 to Aug 2018; the edges are too thin.
- Only 3.0% of customers bought twice, so retention is studied on sellers, not customers.
- 145 sellers sold before 2017 and are excluded from new-seller cohorts.

`dbt build` runs 12 models and 25 data tests, including one-row-per-key tests and two tests that item value reconciles exactly across the raw items and every mart.

## Run it

1. Download the [Olist dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) and unzip the CSVs into `data/raw/`.
2. Install: `pip install -r requirements.txt`
3. Build and test the models: `dbt build --profiles-dir .`
4. Answer the questions: `python scripts/q1_order_experience.py`, `q2_merchant_retention.py`, `q3_segments_and_sizing.py`
5. Check every headline number independently: `python checks/independent_check.py` (14 of 14 pass)
6. Rebuild the report: `python scripts/build_report.py`

## Limits

- Historical marketplace data, not software usage data. It shows orders, deliveries, reviews and seller activity, not feature adoption or website conversion, and no events are invented to fill that gap.
- The seller comparisons are associations, used to rank where to look. A randomized test would measure cause.
- The sizing shares are assumptions, shown with their inputs so they can be changed.
- Sales are item price in reais. Olist's commission is not in the data, so this is sales, not marketplace revenue.
