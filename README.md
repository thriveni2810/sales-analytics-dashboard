# Data-Driven Business Analytics Dashboard

Capstone project of the **SQL and Database Management Systems Virtual Internship** (EduSkills Academy × AICTE, National Internship Portal).
Author: Boddupally Thriveni (23311A05AW) · B.Tech CSE, Sreenidhi Institute of Science and Technology (SNIST), Hyderabad.

The project shows how business data is **stored** (MongoDB), **queried** (aggregation pipeline), **analysed** (Python) and **converted into visual reports** (PNG charts, an interactive web dashboard, and CSV files for Power BI).

---

## 1. Table of contents
1. [Overview](#2-overview)
2. [Features](#3-features)
3. [Tech stack](#4-tech-stack)
4. [Project structure](#5-project-structure)
5. [Architecture / data flow](#6-architecture--data-flow)
6. [Dataset](#7-dataset)
7. [Setup and installation](#8-setup-and-installation)
8. [How to run](#9-how-to-run)
9. [MongoDB aggregation pipelines](#10-mongodb-aggregation-pipelines)
10. [Outputs](#11-outputs)
11. [Web dashboard and GitHub Pages](#12-web-dashboard-and-github-pages)
12. [Power BI dashboard](#13-power-bi-dashboard)
13. [Using your own data](#14-using-your-own-data)
14. [Troubleshooting](#15-troubleshooting)
15. [Concepts demonstrated](#16-concepts-demonstrated)
16. [Future improvements](#17-future-improvements)

## 2. Overview
Organisations need to monitor sales, profit and product performance. This project builds a small end-to-end analytics pipeline:

`orders.csv → MongoDB → aggregation pipelines → CSV / JSON → charts + dashboard`

It can run **with MongoDB** (the intended design) or **without any database** (`--source csv`), which produces identical results, so anyone can reproduce the outputs quickly.

## 3. Features
- Sales and revenue analysis
- Profit and order analysis (total revenue, profit, margin, orders, units)
- Monthly sales performance (Jan–Dec 2025)
- Product category analysis
- Customer purchase analysis (every order carries a customer id)
- Regional sales comparison (North, East, South, West)
- Advanced MongoDB queries using the aggregation pipeline (`$group`, `$sort`, `$limit`, `$dateToString`)
- Four report-style PNG charts, one interactive web dashboard (light/dark aware), CSV exports for Power BI

## 4. Tech stack
| Layer | Technology |
|---|---|
| Database | MongoDB (NoSQL document database) |
| Query engine | MongoDB Aggregation Pipeline |
| Scripting | Python 3.9+ (`pymongo`, `csv`, `json`) |
| Static charts | matplotlib |
| Web dashboard | HTML, CSS, JavaScript, Chart.js 4.4.1 |
| BI tool | Power BI Desktop (via CSV exchange) |

## 5. Project structure
```
sales-analytics-dashboard/
├── data/
│   └── orders.csv                  # generated sales dataset (661 orders)
├── out/                            # generated results
│   ├── monthly_revenue_profit.csv
│   ├── revenue_by_category.csv
│   ├── revenue_by_region.csv
│   ├── top_products_by_units.csv
│   └── output1..4_*.png            # the four report charts
├── docs/                           # web dashboard (GitHub Pages folder)
│   ├── template.html               # dashboard source
│   ├── data.json                   # aggregated data for the dashboard
│   └── index.html                  # built dashboard (template + data)
├── generate_data.py                # creates data/orders.csv
├── seed_mongo.py                   # loads orders.csv into MongoDB
├── analytics.py                    # pipelines + CSV/JSON export (mongo or csv source)
├── charts.py                       # builds the PNG charts
├── build_dashboard.py              # builds docs/index.html
├── requirements.txt
└── README.md
```

## 6. Architecture / data flow
```
generate_data.py ──► data/orders.csv ──► seed_mongo.py ──► MongoDB (sales_db.orders)
                          │                                      │
                          │ (--source csv)                       │ (--source mongo)
                          ▼                                      ▼
                                  analytics.py
                         ┌────────────┴─────────────┐
                    out/*.csv                  docs/data.json
                  (Power BI, charts.py)      (build_dashboard.py)
                         │                          │
                  out/*.png charts          docs/index.html dashboard
```

## 7. Dataset
`data/orders.csv` is **sample data** created by `generate_data.py` (fixed random seed, so it is reproducible). One row per order.

| Column | Description |
|---|---|
| order_id | Unique id, e.g. `ORD00001` |
| order_date | `YYYY-MM-DD`, all in 2025 |
| customer_id | `C001`–`C060` |
| region | North / East / South / West |
| category | Electronics, Furniture, Accessories, Stationery |
| product | Laptop, Smartphone, Monitor, Printer, Desk, Office Chair, Headphones, Backpack, Notebook, Pen Set |
| quantity | Units in the order (1–3) |
| unit_price, unit_cost | Price and cost per unit (₹) |
| revenue | `quantity × unit_price` |
| cost | `quantity × unit_cost` |
| profit | `revenue − cost` |

In MongoDB each row becomes a document in `sales_db.orders`, with `order_date` stored as a real date so `$dateToString` works.

## 8. Setup and installation
Requirements: **Python 3.9+**. MongoDB is optional (only for `--source mongo`).

```bash
git clone <your-repo-url>
cd sales-analytics-dashboard
python -m venv .venv
source .venv/bin/activate         
 # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
MongoDB (optional): install MongoDB Community Server locally, or create a free MongoDB Atlas cluster and copy its connection string.

## 9. How to run
**Option A – without MongoDB (fastest)**
```bash
python generate_data.py
python analytics.py --source csv
python charts.py
python build_dashboard.py
```
**Option B – with MongoDB**
```bash
python generate_data.py
export MONGO_URI="mongodb://localhost:27017"     # Windows: set MONGO_URI=...   (or your Atlas URI)
python seed_mongo.py                              # loads data into sales_db.orders
python analytics.py --source mongo                # runs the aggregation pipelines
python charts.py
python build_dashboard.py
```
Then open `docs/index.html` in a browser.

| Script | What it does | Output |
|---|---|---|
| `generate_data.py` | Builds the dataset | `data/orders.csv` |
| `seed_mongo.py` | Inserts documents, creates indexes on `order_date`, `category`, `region` | MongoDB collection |
| `analytics.py` | Runs the 5 pipelines (or the Python equivalent) | `out/*.csv`, `docs/data.json` |
| `charts.py` | Draws the report charts | `out/output*.png` |
| `build_dashboard.py` | Injects data into the template | `docs/index.html` |

## 10. MongoDB aggregation pipelines
Defined in `analytics.py` and run against `sales_db.orders`.

**Monthly revenue and profit**
```js
db.orders.aggregate([
  { $group: { _id: { $dateToString: { format: "%Y-%m", date: "$order_date" } },
              revenue: { $sum: "$revenue" }, profit: { $sum: "$profit" } } },
  { $sort: { _id: 1 } }
])
```
**Revenue by category** (same idea for region)
```js
db.orders.aggregate([
  { $group: { _id: "$category", revenue: { $sum: "$revenue" } } },
  { $sort: { revenue: -1 } }
])
```
**Top 8 products by units sold**
```js
db.orders.aggregate([
  { $group: { _id: "$product", units: { $sum: "$quantity" } } },
  { $sort: { units: -1 } }, { $limit: 8 }
])
```
**Overall totals (KPI cards)**
```js
db.orders.aggregate([
  { $group: { _id: null, revenue: { $sum: "$revenue" }, profit: { $sum: "$profit" },
              orders: { $sum: 1 }, units: { $sum: "$quantity" } } }
])
```

## 11. Outputs
| # | Output | File | Result with the sample data |
|---|---|---|---|
| 1 | Monthly Revenue and Profit | `out/output1_monthly_revenue_profit.png` | Peak in Oct, dip in Sep, profit ≈ 35% of revenue |
| 2 | Revenue by Product Category | `out/output2_revenue_by_category.png` | Electronics ≫ Furniture > Accessories > Stationery |
| 3 | Revenue by Region | `out/output3_revenue_by_region.png` | North highest, then East, South, West |
| 4 | Top Products by Units Sold | `out/output4_top_products_by_units.png` | Smartphone 148, Laptop 118, Headphones 112 … |

Headline figures (sample data): total revenue ≈ ₹2.68 lakh, 661 orders, ~35% profit margin.

## 12. Web dashboard and GitHub Pages
`docs/index.html` is a single self-contained page (Chart.js loaded from cdnjs) with KPI cards and four interactive charts; it follows the browser's light/dark theme.

Publish it free:
1. Push the repo to GitHub.
2. **Settings → Pages → Build and deployment → Source: Deploy from a branch.**
3. Choose branch `main`, folder **`/docs`**, then Save.
4. Your dashboard appears at `https://<username>.github.io/<repo-name>/`.

Push commands:
```bash
git init
git add .
git commit -m "Data-driven business analytics dashboard"
git branch -M main
git remote add origin https://github.com/<username>/<repo-name>.git
git push -u origin main
```

## 13. Power BI dashboard
1. Open **Power BI Desktop → Get data → Text/CSV**.
2. Import `data/orders.csv` (full data) and/or the files in `out/`.
3. In **Power Query**, check data types (dates, numbers).
4. Build visuals: line chart (month vs revenue/profit), column charts (category, region), bar chart (top products), cards (revenue, profit, orders), and slicers for region, category and year.
5. Optional DAX measures: `Total Revenue = SUM(orders[revenue])`, `Profit Margin = DIVIDE(SUM(orders[profit]), SUM(orders[revenue]))`.
6. Save as `.pbix` and add it to the repo (or export a screenshot to the README).

## 14. Using your own data
Replace `data/orders.csv` with a file that has the **same columns** (section 7), then re-run `seed_mongo.py` (if using MongoDB), `analytics.py`, `charts.py` and `build_dashboard.py`. Skip `generate_data.py`, otherwise it overwrites your file.

## 15. Troubleshooting
| Problem | Fix |
|---|---|
| `ModuleNotFoundError: pymongo` | `pip install -r requirements.txt` |
| `ServerSelectionTimeoutError` | MongoDB is not running or `MONGO_URI` is wrong; or use `--source csv` |
| `FileNotFoundError: data/orders.csv` | Run `python generate_data.py` first and run scripts from the project root |
| Dashboard charts are blank | Check internet access (Chart.js loads from cdnjs); rebuild with `python build_dashboard.py` |
| GitHub Pages shows 404 | Confirm Pages source is `main` + `/docs` and wait a minute for deployment |

## 16. Concepts demonstrated
Relational vs NoSQL thinking · document model and BSON dates · indexing · aggregation pipeline · ETL (extract from CSV, transform to aggregates, load to outputs) · data visualisation · KPI design · reproducible data generation · git/GitHub Pages deployment.

## 17. Future improvements
Interactive filters (region, category, date range) · REST API with Node.js/Express or FastAPI serving the pipelines · Docker Compose with MongoDB · scheduled refresh · customer segmentation and forecasting.

## 18. Acknowledgements
Internship Coordinator **Mr. V. Satheesh Kumar**, HOD **Dr. K. Shirisha**, Principal **Dr. T. Ch. Shiva Reddy**, and EduSkills Academy × AICTE for the virtual internship program.

## 19. License
For academic use. Add a license (for example MIT) if you want others to reuse it.
