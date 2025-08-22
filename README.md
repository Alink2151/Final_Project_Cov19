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

## 13) Windows setup (PowerShell)
- Install Python 3.10+: `winget install Python.Python.3.10`
- Allow venv activation if blocked:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
- Create venv and install deps:
```powershell
cd C:\Dismer\Final_Project_Cov19-main
Copy-Item .env.example .env
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
- Run API and Dashboard:
```powershell
$env:FLASK_APP="app.api:app"
python -m flask run --host 0.0.0.0 --port 8000
# new terminal
.\.venv\Scripts\Activate.ps1
$env:API_BASE="http://localhost:8000/api"
python .\dashboard\app.py
```
- Optional: Docker Desktop for Mongo/Redis: `winget install Docker.DockerDesktop`, then `docker compose up -d`.
- Alternative: Use WSL (`wsl --install -d Ubuntu`) and follow Linux instructions.

## 14) API reference
Base URL: `http://localhost:8000/api`
- `GET /health` — healthcheck
- `GET /timeseries?country=United%20States` — daily new cases (DATE, CASES)
- `GET /forecast?country=United%20States&horizon=14` — SARIMAX forecast with confidence bands
- `GET /clusters?k=5` — k-means labels per country
- `GET /pattern?country=United%20States` — pattern recognition results from `V_PATTERN_SURGE`
- `POST /comments` — body: `{ country, region?, date?, text }`
- `GET /comments?country=...&region=...`

## 15) Troubleshooting
- Flask cannot find app: ensure `FLASK_APP=app.api:app` and run from project root.
- venv activation blocked: run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` and re-open PowerShell.
- Dashboard error `run_server` deprecated: fixed, use latest code with `app.run`.
- Dashboard JSON decode error: check API logs; likely Snowflake views not created or provider DB name differs. Update `SET PROVIDER_DB` in `sql/setup_warehouse_and_views.sql` and re-run scripts.
- Redis connection error: caching is optional; API now fails open without Redis.

## 16) Caching options
- Default `REDIS_URL=redis://redis:6379/0` (Docker). For local Redis on Windows: `redis://localhost:6379/0`.
- Hosted Redis: set `REDIS_URL` to your provider’s URI.
- If Redis is unavailable, API computes fresh results without caching.

## 17) MongoDB schema (comments)
- Collection: `comments`
- Suggested JSON Schema: see `app/mongo_schema.json`
- Example document:
```json
{
  "country": "United States",
  "region": "New York",
  "date": "2021-01-10",
  "text": "Notable surge after holidays",
  "user": "analyst01",
  "created_at": "2021-01-10T12:34:56Z"
}
```

## 18) Data augmentation workflow
- Place demographics CSV at `data/us_states_demographics.csv` with columns: STATE, POPULATION, MEDIAN_AGE, POVERTY_RATE, INCOME.
- Run:
```bash
python eda/augment_with_demographics.py
```
- Creates Snowflake table `US_STATE_DEMOGRAPHICS` and view `V_JHU_US_WITH_DEMOGRAPHICS`.

## 19) Sharing structures (Snowflake Data Share)
- Use `sql/share_structures.sql`. Replace `<BOOTCAMP_ACCOUNT_LOCATOR>` and execute as ACCOUNTADMIN:
```sql
CREATE OR REPLACE SHARE COVID_APP_SHARE;
GRANT USAGE ON DATABASE COVID_APP TO SHARE COVID_APP_SHARE;
GRANT USAGE ON SCHEMA COVID_APP.PUBLIC TO SHARE COVID_APP_SHARE;
GRANT SELECT ON ALL VIEWS IN SCHEMA COVID_APP.PUBLIC TO SHARE COVID_APP_SHARE;
-- ALTER SHARE COVID_APP_SHARE ADD ACCOUNT = <BOOTCAMP_ACCOUNT_LOCATOR>;
```
- Provide the share name and your account locator to the Bootcamp leader so they can create a database from the share.