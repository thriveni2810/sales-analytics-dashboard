"""Create the four report charts as PNGs in out/ (matplotlib)."""
import csv
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
rd = lambda n: list(csv.DictReader(open(f"out/{n}.csv")))
def save(name): plt.tight_layout(); plt.savefig(f"out/{name}.png", dpi=150); plt.close()

d = rd("monthly_revenue_profit"); x = [r["month"] for r in d]
plt.figure(figsize=(10, 4.5))
plt.plot(x, [float(r["revenue"]) for r in d], "o-", label="Revenue")
plt.plot(x, [float(r["profit"]) for r in d], "o-", label="Profit")
plt.title("Monthly Revenue and Profit"); plt.xlabel("Month"); plt.ylabel("Amount (₹)")
plt.xticks(rotation=45); plt.legend(); save("output1_monthly_revenue_profit")
for fn, name, key, lab, title in [("revenue_by_category", "output2_revenue_by_category", "category", "Revenue (₹)", "Revenue by Product Category"),
                                  ("revenue_by_region", "output3_revenue_by_region", "region", "Revenue (₹)", "Revenue by Region"),
                                  ("top_products_by_units", "output4_top_products_by_units", "product", "Units Sold", "Top Products by Units Sold")]:
    d = rd(fn); plt.figure(figsize=(9, 4.5))
    plt.bar([r[key] for r in d], [float(r[lab.split()[0].lower() if lab.startswith("Units") is False else "units"]) for r in d])
    plt.title(title); plt.xlabel(key.capitalize()); plt.ylabel(lab); save(name)
print("Charts saved in out/")
