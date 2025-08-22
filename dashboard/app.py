from __future__ import annotations
import os
import requests
import pandas as pd
from dash import Dash, dcc, html, Input, Output

API_BASE = os.getenv("API_BASE", "http://localhost:8000/api")
COUNTRY_DEFAULT = "United States"

app = Dash(__name__)

app.layout = html.Div([
	html.H2("COVID-19 Dashboard"),
	dcc.Input(id="country", type="text", value=COUNTRY_DEFAULT),
	dcc.Graph(id="ts"),
	dcc.Graph(id="forecast"),
])


@app.callback(Output("ts", "figure"), Input("country", "value"))
def update_ts(country):
	try:
		resp = requests.get(f"{API_BASE}/timeseries", params={"country": country}, timeout=30)
		resp.raise_for_status()
		data = resp.json()
		df = pd.DataFrame(data)
		return {
			"data": [{"x": df.get("DATE", []), "y": df.get("CASES", []), "type": "lines", "name": "Cases"}],
			"layout": {"title": f"Daily Cases - {country}"}
		}
	except Exception as e:
		title = f"Timeseries error: {str(e)}"
		try:
			preview = resp.text[:200] if 'resp' in locals() else ''
		except Exception:
			preview = ''
		return {"data": [], "layout": {"title": title + (f" | {preview}" if preview else "")}}


@app.callback(Output("forecast", "figure"), Input("country", "value"))
def update_fc(country):
	try:
		resp = requests.get(f"{API_BASE}/forecast", params={"country": country, "horizon": 14}, timeout=30)
		resp.raise_for_status()
		data = resp.json()
		df = pd.DataFrame(data)
		return {
			"data": [
				{"x": df.get("DATE", []), "y": df.get("forecast", []), "type": "lines", "name": "Forecast"},
				{"x": df.get("DATE", []), "y": df.get("lower", []), "type": "lines", "name": "Lower", "line": {"dash": "dot"}},
				{"x": df.get("DATE", []), "y": df.get("upper", []), "type": "lines", "name": "Upper", "line": {"dash": "dot"}},
			],
			"layout": {"title": f"Forecast - {country}"}
		}
	except Exception as e:
		title = f"Forecast error: {str(e)}"
		try:
			preview = resp.text[:200] if 'resp' in locals() else ''
		except Exception:
			preview = ''
		return {"data": [], "layout": {"title": title + (f" | {preview}" if preview else "")}}


if __name__ == "__main__":
	app.run(host=os.getenv("DASH_HOST", "0.0.0.0"), port=int(os.getenv("DASH_PORT", "8050")), debug=True)