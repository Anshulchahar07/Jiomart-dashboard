# JioMart Catalogue Insights — Streamlit Dashboard

An interactive dashboard built in Python with Streamlit, styled with custom
HTML/CSS (Space Grotesk + Inter, a warm paper/forest-green/marigold palette)
so it reads as a bespoke retail tool rather than a default template.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints (usually http://localhost:8501).

## What's inside

- **Sidebar filters** — category, price range, rating range, free-text search.
  All charts and tables update live from these.
- **KPI strip** — products in view, average rating, average discount, average
  sale price.
- **Overview tab** — category mix and a price-vs-rating scatter.
- **Pricing & Discounts tab (Insight 1)** — where sale price undercuts market
  price most, discount distribution, average discount by category, and the
  15 deepest current discounts.
- **Ratings & Quality tab (Insight 2)** — rating spread by category, rating
  distribution, and the top/bottom 10 rated products — the clearest signal
  for what's delighting or disappointing customers.
- **Category Explorer tab** — pick one category from a dropdown and drill into
  its product types, price-vs-rating bubble chart (bubble size = discount %),
  and a full sortable table for just that category.
- **Explore Data tab** — the full filtered table with a CSV download.

The Overview tab also includes an average-price-by-category bar chart and a
treemap sized by product count and colored by average rating.

`.streamlit/config.toml` pins a light theme so the dashboard's text stays
fully readable regardless of your OS/browser dark-mode setting.

## Files

- `app.py` — the dashboard
- `data.csv` — cleaned product catalogue (1,026 rows: product, category,
  sale price, market price, type, rating)
- `requirements.txt` — Python dependencies
