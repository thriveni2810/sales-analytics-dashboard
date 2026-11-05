"""Load data/orders.csv into MongoDB (db: sales_db, collection: orders)."""
import csv, os
from datetime import datetime
from pymongo import MongoClient
uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
col = MongoClient(uri)["sales_db"]["orders"]
col.drop()
docs = []
for r in csv.DictReader(open("data/orders.csv")):
    for k in ("quantity", "unit_price"): r[k] = int(r[k])
    for k in ("unit_cost", "revenue", "cost", "profit"): r[k] = float(r[k])
    r["order_date"] = datetime.strptime(r["order_date"], "%Y-%m-%d")
    docs.append(r)
col.insert_many(docs)
col.create_index("order_date"); col.create_index("category"); col.create_index("region")
print(f"Inserted {len(docs)} documents into sales_db.orders")
