"""Generate a reproducible sample sales dataset (data/orders.csv)."""
import csv, random
random.seed(42)
MONTHS = [f"2025-{m:02d}" for m in range(1, 13)]
MW = [28.3, 28.3, 23.9, 11.4, 19.7, 18.4, 19.0, 23.4, 7.0, 35.7, 22.8, 30.0]
REGIONS = ["North", "East", "South", "West"]
RW = [79.7, 67.6, 62.2, 58.7]
COST = {"Electronics": .66, "Furniture": .62, "Accessories": .60, "Stationery": .55}
PRODUCTS = [("Laptop","Electronics",1050,118),("Smartphone","Electronics",520,148),
            ("Monitor","Electronics",160,93),("Printer","Electronics",125,101),
            ("Desk","Furniture",250,80),("Office Chair","Furniture",140,95),
            ("Headphones","Accessories",35,112),("Backpack","Accessories",22,95),
            ("Notebook","Stationery",8,70),("Pen Set","Stationery",6,60)]

def split(total, weights):
    s = sum(weights); raw = [total * w / s for w in weights]; out = [int(x) for x in raw]
    order = sorted(range(len(raw)), key=lambda i: raw[i] - out[i], reverse=True)
    for i in order[:total - sum(out)]: out[i] += 1
    return out

rows = []
for name, cat, price, units in PRODUCTS:
    for m, um in zip(MONTHS, split(units, MW)):
        for r, ur in zip(REGIONS, split(um, RW)):
            while ur > 0:
                q = min(ur, random.randint(1, 3)); ur -= q
                cost = round(price * COST[cat], 2)
                rows.append([f"{m}-{random.randint(1,28):02d}", f"C{random.randint(1,60):03d}", r, cat,
                             name, q, price, cost, q * price, round(q * cost, 2), round(q * (price - cost), 2)])
rows.sort(key=lambda x: x[0])
with open("data/orders.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["order_id","order_date","customer_id","region","category","product",
                "quantity","unit_price","unit_cost","revenue","cost","profit"])
    for i, r in enumerate(rows, 1): w.writerow([f"ORD{i:05d}"] + r)
print(f"Wrote {len(rows)} orders to data/orders.csv")
