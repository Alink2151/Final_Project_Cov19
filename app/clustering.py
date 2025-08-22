from __future__ import annotations
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


def cluster_regions(df: pd.DataFrame, n_clusters: int = 5) -> pd.DataFrame:
	features = df[["cases_per_100k", "deaths_per_100k", "growth_rate"]].fillna(0)
	scaled = StandardScaler().fit_transform(features)
	labels = KMeans(n_clusters=n_clusters, n_init=10, random_state=42).fit_predict(scaled)
	out = df.copy()
	out["cluster"] = labels
	return out