# Technical Assessment

## Overview

This project implements a **Pricing Intelligence Platform** designed to help **merchandisers and buyers** analyze product pricing and make informed decisions based on competitor data.

The system ingests product and competitor data from a CSV file, stores it in a structured database, and provides:

* **Analytics Dashboard** for pricing insights
* **Buyer Interface** for product comparison and decision-making

---

## Key Features

### 🔹 Data Ingestion

* Automated CSV ingestion into SQLite database
* Data cleaning and transformation pipeline
* Handles missing values, duplicates, and type conversion

---

### 🔹 Pricing Analytics

* Price index calculation
* Competitor comparison
* Filtering across:

  * Category
  * Segment
  * Collection
  * Product Type

---

### 🔹 Buyer Decision Tool

* Search products by name
* View product cards with:

  * Image
  * Product link
  * Price per unit
* Expandable competitor comparison:

  * Sorted by cheapest price per unit
  * Direct links to competitor listings

---

### 🔹 Interactive Dashboard (Dash)

* Multi-page application:

  * Overview Dashboard
  * Buyer Page
* Dynamic filters with dependency handling
* Clean and intuitive UI for quick insights

---

## Project Structure

```
pricing-intelligence-platform/

├── app/
│   ├── api/
│   │    └── routes.py
│   │
│   ├── dashboard/
│   │    ├── dash_app.py
│   │    └── pages/
│   │         ├── merchandiser.py
│   │         └── buyer.py
│   │
│   ├── ingestion/
│   │    └── csv_loader.py
│   │
│   ├── database/
│   │    ├── models.py
│   │    └── db.py
│   │
│   └── services/
│        └── pricing.py
│
├── data/
│    └── pricing_data.csv
│
├── DECISIONS.md
├── README.md
├── requirements.txt
└── main.py
```

---

## Tech Stack

* **Backend:** FastAPI
* **Frontend:** Dash (Plotly)
* **Database:** SQLite
* **Data Processing:** Pandas

---

## Data Processing

Key cleaning steps:

* Removed irrelevant columns (index & empty columns)
* Dropped rows with missing critical pricing data
* Converted numeric columns to proper types
* Removed duplicate product–competitor pairs
* Standardized pricing using:

  * `price_per_unit_combined`
* Recalculated `price_index` for consistency

---

## Core Concepts

### 🔹 Price Index

Measures how a product compares to competitors:

```
price_index = DIY Price / Competitor Price
```

---

### 🔹 Price per Unit

Used for fair comparison across different packaging sizes.

---

## How to Run

### 1. Install dependencies

```
pip install -r requirements.txt
```

---

### 2. Run Data Ingestion & API Server

```
uvicorn main:app --reload --port 8080
```

This will:

* Load CSV from `/data`
* Clean and transform data
* Insert into SQLite database

---

### 3. Run Dashboard

```
python app/dashboard/dash_app.py
```

---

## Application Pages

### Overview Dashboard

* High-level pricing insights
* Filterable across product dimensions

---

### Buyer Page

* Search and filter products
* View product cards
* Compare competitor pricing
* Identify best-value options

---

## Limitations

* SQLite not suitable for large-scale or concurrent workloads
* No vendor name normalization (duplicates may exist)
* Limited unit standardization
* No recommendation engine (yet)
* No real-time data updates

---

## 🔮 Future Improvements

* Pricing recommendation engine
* Competitor name normalization (fuzzy matching)
* Unit standardization layer
* Advanced analytics (distribution, outliers)
* UI enhancements (badges, highlights, insights)
* Deployment (Docker / cloud)

---

## Target Users

* **Merchandisers**

  * Monitor competitiveness
  * Adjust pricing strategies

* **Buyers**

  * Compare products
  * Identify best-value purchases

---

## Design Philosophy

This project focuses on:

* Simplicity over complexity
* Clear data flow (CSV → DB → API → UI)
* Practical decision-making tools
* Extensibility for future improvements

---

## Additional Documentation

* `DECISIONS.md` → Detailed explanation of design choices and trade-offs

---

## Summary

This platform demonstrates:

* End-to-end data pipeline design
* Backend API development
* Database modeling
* Interactive dashboard creation
* Real-world decision support system

---

**Built for technical assessment with focus on clarity, scalability, and practical business use cases.**
