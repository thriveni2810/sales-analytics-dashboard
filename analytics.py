"""Run the analytics. --source mongo uses MongoDB aggregation pipelines;
--source csv computes identical results in pure Python (no database needed).
Writes out/*.csv (for Power BI) and docs/data.json (for the web dashboard)."""
import argparse, csv, json, os
from collections import defaultdict

SUM = lambda f: {"$sum": f}
PIPELINES = {
    "monthly_revenue_profit": [
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m", "date": "$order_date"}},
                    "revenue": SUM("$revenue"), "profit": SUM("$profit")}},
        {"$sort": {"_id": 1}}],
    "revenue_by_category": [
        {"$group": {"_id": "$category", "revenue": SUM("$revenue")}}, {"$sort": {"revenue": -1}}],
    "revenue_by_region": [
        {"$group": {"_id": "$region", "revenue": SUM("$revenue")}}, {"$sort": {"revenue": -1}}],
    "top_products_by_units": [
        {"$group": {"_id": "$product", "units": SUM("$quantity")}},
        {"$sort": {"units": -1}}, {"$limit": 8}],
    "totals": [
        {"$group": {"_id": None, "revenue": SUM("$revenue"), "profit": SUM("$profit"),
                    "orders": SUM(1), "units": SUM("$quantity")}}],
}

def from_mongo():
    from pymongo import MongoClient
    col = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))["sales_db"]["orders"]
    return {k: [(d["_id"], *[v for kk, v in d.items() if kk != "_id"]) for d in col.aggregate(p)]
            for k, p in PIPELINES.items()}

def from_csv():
    rows = list(csv.DictReader(open("data/orders.csv")))
    agg = lambda key, val: defaultdict(float)
    m, c, r, p = (defaultdict(lambda: [0.0, 0.0]) for _ in range(4))
    cat, reg, units = defaultdict(float), defaultdict(float), defaultdict(int)
    for x in rows:
        mm = m[x["order_date"][:7]]; mm[0] += float(x["revenue"]); mm[1] += float(x["profit"])
        cat[x["category"]] += float(x["revenue"]); reg[x["region"]] += float(x["revenue"])
        units[x["product"]] += int(x["quantity"])
    desc = lambda d: sorted(d.items(), key=lambda kv: -kv[1])
    return {
        "monthly_revenue_profit": [(k, v[0], v[1]) for k, v in sorted(m.items())],
        "revenue_by_category": desc(cat), "revenue_by_region": desc(reg),
        "top_products_by_units": desc(units)[:8],
        "totals": [(None, sum(float(x["revenue"]) for x in rows), sum(float(x["profit"]) for x in rows),
                    len(rows), sum(int(x["quantity"]) for x in rows))]}

ap = argparse.ArgumentParser(); ap.add_argument("--source", choices=["csv", "mongo"], default="csv")
res = (from_mongo if ap.parse_args().source == "mongo" else from_csv)()
os.makedirs("out", exist_ok=True); os.makedirs("docs", exist_ok=True)
heads = {"monthly_revenue_profit": ["month", "revenue", "profit"], "revenue_by_category": ["category", "revenue"],
         "revenue_by_region": ["region", "revenue"], "top_products_by_units": ["product", "units"]}
for k, h in heads.items():
    with open(f"out/{k}.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(h); w.writerows([[a, *[round(v, 2) for v in rest]] for a, *rest in res[k]])
t = res["totals"][0]
data = {"kpi": {"revenue": t[1], "profit": t[2], "orders": t[3], "units": t[4]},
        **{k: [[a, *[round(v, 2) for v in rest]] for a, *rest in res[k]] for k in heads}}
json.dump(data, open("docs/data.json", "w"), indent=1)
print("Done:", {k: len(v) for k, v in res.items()})
