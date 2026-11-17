# Independent check of every headline number.
# Written separately from the dbt models: pandas straight from the raw CSVs, no shared code.
import pandas as pd
from pathlib import Path

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
orders = pd.read_csv(RAW / "olist_orders_dataset.csv", parse_dates=["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"])
items = pd.read_csv(RAW / "olist_order_items_dataset.csv")
reviews = pd.read_csv(RAW / "olist_order_reviews_dataset.csv", parse_dates=["review_answer_timestamp", "review_creation_date"])

results = []
def check(label, got, expected, tol=0.05):
    ok = abs(got - expected) <= tol
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {label}: got {got:,.2f}, expected {expected:,.2f}")

# Window: orders placed Jan 2017 to Aug 2018
o = orders[(orders.order_purchase_timestamp >= "2017-01-01") & (orders.order_purchase_timestamp < "2018-09-01")].copy()

# Q1. One row = one order
check("Orders in window", len(o), 99092, 0)
check("Failed %", 100 * o.order_status.isin(["canceled", "unavailable"]).mean(), 1.19, 0.005)
d = o[o.order_delivered_customer_date.notna()].copy()
d["late"] = d.order_delivered_customer_date.dt.normalize() > d.order_estimated_delivery_date
check("Delivered with a date", len(d), 96204, 0)
check("Late %", 100 * d.late.mean(), 6.79, 0.005)

# Reviews: keep the most recent answer per order
r = (reviews.sort_values(["order_id", "review_answer_timestamp", "review_creation_date", "review_id"],
                         ascending=[True, False, False, True])
            .drop_duplicates("order_id"))
dr = d.merge(r[["order_id", "review_score"]], on="order_id")
check("Avg review, late", dr[dr.late].review_score.mean(), 2.27, 0.005)
check("Avg review, on time", dr[~dr.late].review_score.mean(), 4.29, 0.005)

# Q2 and Q3. One row = one seller's part of one order -> one seller-month
so = items.merge(orders[["order_id", "order_purchase_timestamp"]], on="order_id")
so["month"] = so.order_purchase_timestamp.dt.to_period("M")
old_sellers = set(so[so.order_purchase_timestamp < "2017-01-01"].seller_id)
win = so[(so.order_purchase_timestamp >= "2017-01-01") & (so.order_purchase_timestamp < "2018-09-01")]
sm = win.groupby(["seller_id", "month"]).agg(orders=("order_id", "nunique"), value=("price", "sum")).reset_index()
first = sm.groupby("seller_id").month.min().rename("cohort")
sm = sm.join(first, on="seller_id")
sm["k"] = (sm.month - sm.cohort).apply(lambda x: x.n)
new = sm[~sm.seller_id.isin(old_sellers)]

# Came back within months 1 to 3, cohorts up to May 2018
cohorts = first[~first.index.isin(old_sellers)]
c3 = cohorts[cohorts <= pd.Period("2018-05", "M")]
back = new[(new.k.between(1, 3))].seller_id.unique()
check("Came back within 3 months %", 100 * c3.index.isin(back).mean(), 75.9, 0.05)

# Value held by sellers active 7+ months (all sellers with an order in the window)
months_active = sm.groupby("seller_id").month.nunique()
value = sm.groupby("seller_id").value.sum()
check("Value share, sellers active 7+ months %", 100 * value[months_active >= 7].sum() / value.sum(), 80.4, 0.05)

# Segments, cohorts Jan 2017 to Feb 2018
c6 = cohorts[cohorts <= pd.Period("2018-02", "M")]
m0 = new[new.k == 0].set_index("seller_id").orders.reindex(c6.index)
v6 = new[new.k.between(1, 6)].groupby("seller_id").value.sum().reindex(c6.index).fillna(0)
seg = pd.cut(m0, [0, 1, 4, 10**9], labels=["1", "2-4", "5+"])
check("1-order starters", (seg == "1").sum(), 1138, 0)
check("2-4 order starters", (seg == "2-4").sum(), 611, 0)
check("5+ order starters", (seg == "5+").sum(), 178, 0)
check("Avg 6-month sales, 1-order", v6[seg == "1"].mean(), 1357, 0.5)
check("Avg 6-month sales, 2-4 order", v6[seg == "2-4"].mean(), 2629, 0.5)
starters_2017 = ((seg == "1") & (c6.dt.year == 2017)).sum() if hasattr(c6, "dt") else ((seg == "1") & (c6.map(lambda p: p.year) == 2017)).sum()
check("1-order starters in 2017", starters_2017, 983, 0)

print(f"\n{sum(results)} of {len(results)} checks pass")
assert all(results)
