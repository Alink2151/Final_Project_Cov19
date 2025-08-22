# COVID-19 Analytics Platform (Snowflake + Flask API + MongoDB + Dash)

## 1) Snowflake Trial Setup (AWS us-east-2 Ohio)
- Go to `https://signup.snowflake.com/`
- Choose Cloud: AWS, Region: US East (Ohio) us-east-2, Edition: Standard (or higher)
- Create account. After activation, sign in as ACCOUNTADMIN (or create a role with needed privileges).
- From Marketplace, subscribe to "COVID-19 Epidemiological Data" by Starschema (free). Note the provided database name, e.g., `COVID19_BY_STARSCHEMA`.

## 2) Local Prerequisites
- Python 3.10+
- Optional: Docker (for MongoDB and Redis). If you don't have Docker, install MongoDB and Redis locally and update `.env` accordingly.

## 3) Project Setup
```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# If using Docker services for Mongo/Redis:
docker compose up -d
```

## 4) Configure Environment
Update `.env` with your Snowflake credentials and database details. Ensure:
- `SNOWFLAKE_WAREHOUSE=COVID_WH` (created by our SQL below)
- `SNOWFLAKE_DATABASE=COVID_APP` (our working DB holding views)
- `SNOWFLAKE_SCHEMA=PUBLIC`
- `SNOWFLAKE_ROLE=SYSADMIN` (or role with privileges)
- `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD` set.

## 5) Initialize Snowflake Objects
Run the SQL scripts under `sql/` in order, using Snowsight or SnowSQL:
1. `sql/setup_resource_monitor.sql` — creates a resource monitor and assigns it to the warehouse.
2. `sql/setup_warehouse_and_views.sql` — creates warehouse, database, schema, and convenience views over Starschema data.

## 6) Run the API and Dashboard
```bash
# In one terminal (API)
export $(grep -v '^#' .env | xargs) ; FLASK_APP=app.api:app flask run --host "$API_HOST" --port "$API_PORT"

# In another terminal (Dashboard)
export $(grep -v '^#' .env | xargs) ; python dashboard/app.py
```
API base: `http://localhost:8000`
Dashboard: `http://localhost:8050`

## 7) EDA Automation
```bash
export $(grep -v '^#' .env | xargs) ; python eda/eda_automation.py
```
Generates summary CSVs and a simple HTML report under `eda/output/`.

## 8) Report Generation
```bash
export $(grep -v '^#' .env | xargs) ; python report/generate_report.py --out report/Covid_Project_Report.docx
```

## 9) Share Structures with Bootcamp Account
- Edit `sql/setup_warehouse_and_views.sql` bottom section and `sql/share_structures.sql` (if present) to include the target account locator.
- Execute to create a Snowflake data share exposing your `COVID_APP` database/views.

## 10) Security Notes
- Prefer key-pair auth for Snowflake in production.
- Keep `.env` out of version control.

## 11) Project Structure
```
app/                 # Flask API
  api.py             # App factory and server entry
  config.py          # Env config
  snowflake_client.py
  mongo_client.py
  cache.py
  forecasting.py
  clustering.py
  routes.py
  utils.py

sql/                 # Snowflake SQL scripts
  setup_resource_monitor.sql
  setup_warehouse_and_views.sql
  pattern_recognition.sql

eda/
  eda_automation.py
  output/

dashboard/
  app.py

report/
  generate_report.py

requirements.txt
.env.example
Dockerfile (optional)
docker-compose.yml
README.md
```

## 12) Notes on Starschema Tables
Names may vary over time. This project references common ones like `JHU_GLOBAL` and `JHU_US`. If views fail to create, query `INFORMATION_SCHEMA.TABLES` under the provider DB to identify current names and adjust `sql/setup_warehouse_and_views.sql` accordingly.