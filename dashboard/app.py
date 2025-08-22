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
	resp = requests.get(f"{API_BASE}/timeseries", params={"country": country}, timeout=30)
	df = pd.DataFrame(resp.json())
	return {
		"data": [{"x": df["DATE"], "y": df["CASES"], "type": "lines", "name": "Cases"}],
		"layout": {"title": f"Daily Cases - {country}"}
	}


@app.callback(Output("forecast", "figure"), Input("country", "value"))
def update_fc(country):
	resp = requests.get(f"{API_BASE}/forecast", params={"country": country, "horizon": 14}, timeout=30)
	df = pd.DataFrame(resp.json())
	return {
		"data": [
			{"x": df["DATE"], "y": df["forecast"], "type": "lines", "name": "Forecast"},
			{"x": df["DATE"], "y": df["lower"], "type": "lines", "name": "Lower", "line": {"dash": "dot"}},
			{"x": df["DATE"], "y": df["upper"], "type": "lines", "name": "Upper", "line": {"dash": "dot"}},
		],
		"layout": {"title": f"Forecast - {country}"}
	}


if __name__ == "__main__":
	app.run_server(host=os.getenv("DASH_HOST", "0.0.0.0"), port=int(os.getenv("DASH_PORT", "8050")), debug=True)