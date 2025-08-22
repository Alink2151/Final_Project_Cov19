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

## 13) API Reference
Base URL: `http://localhost:${API_PORT:-8000}/api`

- Health
  - GET `/health`
  - 200 → `{ "status": "ok" }`

- Timeseries
  - GET `/timeseries?country=United%20States`
  - Returns array of records with fields: `DATE`, `CASES`
  - Example:
    ```bash
    curl "http://localhost:8000/api/timeseries?country=United%20States"
    ```

- Forecast
  - GET `/forecast?country=United%20States&horizon=14`
  - Returns array with fields: `DATE`, `forecast`, `lower`, `upper`
  - Example:
    ```bash
    curl "http://localhost:8000/api/forecast?country=United%20States&horizon=14"
    ```

- Clusters
  - GET `/clusters?k=5`
  - Returns country-level metrics plus `cluster` label; fields include: `COUNTRY_REGION`, `total_cases`, `total_deaths`, `avg_daily_cases`, `cases_per_100k`, `deaths_per_100k`, `growth_rate`, `cluster`
  - Example:
    ```bash
    curl "http://localhost:8000/api/clusters?k=5"
    ```

- Pattern Recognition
  - GET `/pattern?country=United%20States`
  - Returns rows from `V_PATTERN_SURGE` for the given country

- Comments
  - POST `/comments`
    - Body (JSON): `{ "country": "United States", "region": null, "date": "2021-01-01", "text": "Insight..." }`
    - 200 → `{ "inserted_id": "..." }`
    - Example:
      ```bash
      curl -X POST http://localhost:8000/api/comments \
        -H 'Content-Type: application/json' \
        -d '{"country":"United States","date":"2021-01-01","text":"Insight"}'
      ```
  - GET `/comments?country=United%20States&region=CA`
    - Returns list of comment documents


## 14) Environment Variables
- Snowflake
  - `SNOWFLAKE_ACCOUNT` (required)
  - `SNOWFLAKE_USER` (required)
  - `SNOWFLAKE_PASSWORD` (required)
  - `SNOWFLAKE_ROLE` (default: `SYSADMIN`)
  - `SNOWFLAKE_WAREHOUSE` (default: `COVID_WH`)
  - `SNOWFLAKE_DATABASE` (default: `COVID_APP`)
  - `SNOWFLAKE_SCHEMA` (default: `PUBLIC`)
- API/App
  - `API_HOST` (default: `0.0.0.0`)
  - `API_PORT` (default: `8000`)
  - `SECRET_KEY` (default: `change-me`)
  - `FLASK_ENV` (default: `development`)
  - `FLASK_DEBUG` (default: `0`; set `1` to enable debug)
- Dashboard
  - `DASH_HOST` (default: `0.0.0.0`)
  - `DASH_PORT` (default: `8050`)
  - `API_BASE` (default used by Dash: `http://localhost:8000/api`)
- MongoDB
  - `MONGO_URI` (default: `mongodb://localhost:27017`)
  - `MONGO_DB` (default: `covid_app`)
- Redis
  - `REDIS_URL` (default: `redis://localhost:6379/0`)
- Reporting
  - `STUDENT_NAME` (used in generated DOCX report)


## 15) Docker and Local Services
- Start MongoDB and Redis locally via Docker:
  ```bash
  docker compose up -d
  ```
- Containers expose default ports `27017` (Mongo) and `6379` (Redis). The app defaults target `localhost`, so no extra config is needed when running locally with Compose.
- If using remote services, set `MONGO_URI` and `REDIS_URL` accordingly.


## 16) Dashboard Notes
- Run with: `python dashboard/app.py` (ensure `.env` is loaded so `API_BASE` is correct if your API runs on a different host/port).
- Interactive components:
  - Country input field drives both time series and forecast graphs.


## 17) EDA Outputs
Running `eda/eda_automation.py` produces files under `eda/output/`:
- `profiles.json` — schema profiles for key views
- `global_timeseries.csv` — aggregated by `COUNTRY_REGION, DATE`
- `summary.html` — simple HTML summary


## 18) Troubleshooting
- Missing env var at startup:
  - The app raises: "Missing required environment variable"; ensure `.env` is populated or variables are exported in the shell.
- Snowflake connection errors:
  - Verify `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, and that the role/warehouse/database exist.
  - Ensure Starschema view names used in SQL exist in your provider DB; adjust `sql/setup_warehouse_and_views.sql` if needed.
- Redis `Connection refused`:
  - Start Redis (`docker compose up -d`) or update `REDIS_URL`.
- MongoDB `Connection refused`:
  - Start MongoDB (`docker compose up -d`) or update `MONGO_URI`.
- Dashboard cannot reach API (CORS/network):
  - CORS is enabled. Ensure `API_BASE` points to your API (e.g., `http://localhost:8000/api`).
- Slow forecasts:
  - Reduce `horizon` parameter or pre-cache results.


## 19) Example `.env`
```bash
# Snowflake
SNOWFLAKE_ACCOUNT=abc-xy123
SNOWFLAKE_USER=my_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ROLE=SYSADMIN
SNOWFLAKE_WAREHOUSE=COVID_WH
SNOWFLAKE_DATABASE=COVID_APP
SNOWFLAKE_SCHEMA=PUBLIC

# API/Dashboard
API_HOST=0.0.0.0
API_PORT=8000
DASH_HOST=0.0.0.0
DASH_PORT=8050
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=change-me
API_BASE=http://localhost:8000/api

# Mongo/Redis
MONGO_URI=mongodb://localhost:27017
MONGO_DB=covid_app
REDIS_URL=redis://localhost:6379/0

# Report
STUDENT_NAME=Ada Lovelace
```

## 20) Database Schemas and Models

### Snowflake (Analytical Store)
- **Database/Schema**: `COVID_APP.PUBLIC`
- **Views** (proxied from Starschema provider):
  - `V_JHU_GLOBAL` → mirrors provider `JHU_GLOBAL`
    - Fields commonly used by this app:
      - `DATE` (DATE)
      - `COUNTRY_REGION` (STRING)
      - `PROVINCE_STATE` (STRING, nullable)
      - `NEW_CONFIRMED` (NUMBER)
      - `NEW_DEATHS` (NUMBER)
    - Typical keys: [`COUNTRY_REGION`, `PROVINCE_STATE`, `DATE`]
    - Example usage: time series aggregation by `DATE`, country-level clustering via sums/averages
  - `V_JHU_US` → mirrors provider `JHU_US` (county-level granularity)

- **Pattern Recognition View**: `V_PATTERN_SURGE`
  - Built via `MATCH_RECOGNIZE` over `V_JHU_GLOBAL`
  - Columns (output):
    - `COUNTRY_REGION` (STRING)
    - `START_DATE` (DATE) — first date in detected surge
    - `END_DATE` (DATE) — last date in detected surge
    - `AVG_CASES` (FLOAT) — average `NEW_CONFIRMED` across the surge window
  - Partitioned by `COUNTRY_REGION`, ordered by `DATE`

Note: The Starschema provider may evolve field names. If a view breaks, query `INFORMATION_SCHEMA.TABLES` on the provider DB and adjust `sql/setup_warehouse_and_views.sql` accordingly.

### MongoDB (Operational Store)
- **Database**: from `MONGO_DB` (default `covid_app`)
- **Collection**: `comments`
- **Document schema** (see `app/mongo_schema.json`):
  - `country`: string (required)
  - `region`: string | null (optional)
  - `date`: string | null (ISO date, optional)
  - `text`: string (required)
  - `created_at`: string | null (ISO timestamp, optional)
  - `user`: string | null (optional)
  - Mongo `_id`: ObjectId (auto-generated)
- **Recommended index (optional)**:
  - Compound index on `{ country: 1, region: 1, date: 1 }` to speed reads by filters used in `/api/comments`
- **Example document**:
  ```json
  {
    "_id": "65f1a6...",
    "country": "United States",
    "region": null,
    "date": "2021-01-01",
    "text": "Case surge likely due to holidays.",
    "created_at": "2021-01-02T10:00:00Z",
    "user": "analyst01"
  }
  ```

### Redis (Caching Layer)
- **Connection**: `REDIS_URL` (default `redis://localhost:6379/0`)
- **Key pattern**: `covid:{namespace}:{sha1(json(key_obj))}`
  - Namespace examples: `sql`
  - TTL defined by caller (e.g., timeseries uses `3600` seconds)
- **Value**: JSON-serialized response payloads used by the API