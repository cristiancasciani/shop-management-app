# Circuito — shop management app

A demo inventory manager for **Circuito**, an imaginary electronics shop.
Personal demo project by [Cristian Casciani](https://cristiancasciani.github.io/).

**Stack:** Python · Flask · SQLite · JavaScript (no frontend framework) · openpyxl

## Features

- **Login** with a demo account (`demo` / `demo123`) and CSRF protection on every form.
- **Products:** create, edit and delete; live search, filters (category, brand, stock status), sorting and paging without page reloads.
- **Stock movements:** stock in, stock out and adjustments with a reason and a note; full history per product. Stock can never go negative.
- **Dashboard:** key figures, units in/out over the last 30 days, stock value by category (hand-made SVG charts with tooltips and a table view), reorder list, latest movements.
- **Export** the filtered inventory to Excel (.xlsx) or CSV.
- **Italian / English** interface.
- **Responsive** layout for phones.
- **Demo reset:** one click recreates the sample data (40 products, 60 days of history).

## Run locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/flask --app wsgi run --debug      # http://127.0.0.1:5000
```

The SQLite database is created and filled with demo data on first start (`instance/shop.db`).
Delete that file, or use *Reset demo data* in the app, to start over.

## Tests

```bash
.venv/bin/pip install pytest
.venv/bin/python -m pytest
```

## Project structure

```
app/
  __init__.py     app factory, template helpers, CSRF, language switch
  auth.py         login / logout
  views.py        dashboard, products, movements, exports
  db.py           SQLite connection, schema, demo data generator
  schema.sql      tables
  seed_data.py    demo catalogue
  i18n.py         Italian and English texts
  templates/      Jinja templates
  static/         CSS, JavaScript (charts.js draws the dashboard charts)
tests/            pytest suite
render.yaml       deploy on Render (free plan)
```

## Deploy

`render.yaml` describes a free Render web service (`gunicorn wsgi:app`).
The free plan sleeps when idle: the first visit after a pause takes about 30 seconds.

---
Circuito is fictional. Product names belong to their respective brands and are used only as sample data.
