# Question 3: merchant segments and sizing

Run: `python -I scripts/q3_segments_and_sizing.py` after `dbt build`. Currency: Brazilian reais (R$). Value = item price, not marketplace revenue: Olist's commission is not in the data.

## Answer

Most new sellers (59%) start with a single order, and they are the largest segment to work on. Moving some of them to a stronger first month is worth about R$63,000 a year in the base case, roughly 1% of 2017 sales. That is real but modest: it justifies cheap, automated onboarding help, not a large program.

## Segments

One row = one new seller (no order before Jan 2017), cohorts Jan 2017 to Feb 2018 so each has 6 full months of follow-up.

| First-month size | Sellers | Share | Sold again within 6 months | Avg sales next 6 months | Median |
|---|---|---|---|---|---|
| 1 order | 1,138 | 59.1% | 75.1% | R$1,357 | R$309 |
| 2 to 4 orders | 611 | 31.7% | 89.9% | R$2,629 | R$1,008 |
| 5+ orders | 178 | 9.2% | 98.3% | R$10,347 | R$4,546 |

## Sizing

Opportunity per year = one-order starters per year × share moved × gap × share of the gap that is real.

- One-order starters in 2017: 983.
- Gap in average 6-month sales between 2 to 4 order and 1-order starters: R$1,272.
- The gap is an association. Sellers who start bigger may simply have better products, so only part of it is credited.

| Case | Share moved | Share of gap credited | Opportunity per year |
|---|---|---|---|
| Low | 5% | 25% | R$15,600 |
| Base | 10% | 50% | R$62,500 |
| High | 20% | 75% | R$187,600 |

For scale, all item sales in 2017 were R$6.16M. The base case is about 1% of that.

## Reading it

1. **The segment is big, the money per seller is small.** One-order starters are 59% of new sellers but the median one sells only R$309 in the next six months.
2. **Size the work to the prize.** At about 1% of sales in the base case, the right fix is low-cost and automated: a first-month checklist, a nudge after the first sale, a check on the first review. A staffed onboarding team would not pay back.
3. **The long tail matters less than the top.** 5+ order starters are 9% of new sellers and bring in R$1.84M over six months, more than the 1-order group's R$1.54M. Keeping them is worth as much attention as moving the small starters up.

## Limits

- Averages are pulled up by a few large sellers. Using medians, the gap is R$699 instead of R$1,272, so the base case would be about R$34,000.
- Six months understates lifetime value for sellers who stay longer.
- The low, base and high shares are assumptions, not observed results. A test that randomly offers onboarding help to half of new sellers would measure the real share.
