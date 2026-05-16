from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

import pandas as pd
import requests


USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json"
}


def fetch_earthquakes(
    days_back: int = 7,
    min_magnitude: float = 2.5,
    limit: int = 1000,
) -> pd.DataFrame:
    
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=days_back)

    params = {
        "format": "geojson",
        "starttime": start_time.strftime("%Y-%m-%d"),
        "endtime": end_time.strftime("%Y-%m-%d"),
        "minmagnitude": min_magnitude,
        "limit": limit,
        "orderby": "time",  # mais recentes primeiro
    }

    response = requests.get(USGS_URL, params=params, headers=HEADERS, timeout=30)
    response.raise_for_status()

    data = response.json()
    return _parse_geojson(data)


def _parse_geojson(geojson: dict) -> pd.DataFrame:
    """Transforma o GeoJSON da USGS em um DataFrame tabular limpo."""
    registros = []
    for feature in geojson.get("features", []):
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"]  # [lon, lat, depth]

        registros.append({
            "time": pd.to_datetime(props["time"], unit="ms"),
            "place": props.get("place") or "Localização desconhecida",
            "magnitude": props.get("mag"),
            "depth_km": coords[2],
            "lat": coords[1],
            "lon": coords[0],
            "url": props.get("url"),
            "tsunami": bool(props.get("tsunami", 0)),
            "type": props.get("type", "earthquake"),
        })

    df = pd.DataFrame(registros)

    if not df.empty:
        # Limpeza básica que sempre fazemos
        df = df.dropna(subset=["magnitude", "lat", "lon"])
        df = df.sort_values("time", ascending=False).reset_index(drop=True)

        # Feature engineering simples — útil no dashboard
        df["region"] = df["place"].str.split(",").str[-1].str.strip()
        df["hour"] = df["time"].dt.hour
        df["date"] = df["time"].dt.date

    return df


def get_summary_stats(df: pd.DataFrame) -> dict:
    """KPIs prontos para o dashboard."""
    if df.empty:
        return {"total": 0, "max_mag": 0, "avg_mag": 0, "tsunamis": 0, "latest": None}

    return {
        "total": len(df),
        "max_mag": float(df["magnitude"].max()),
        "avg_mag": float(df["magnitude"].mean()),
        "tsunamis": int(df["tsunami"].sum()),
        "latest": df.iloc[0]["time"],
    }

if __name__ == "__main__":
    print('🌎 Eventos sísmicos nos últimos 7 dias')
    df = fetch_earthquakes(days_back=7, min_magnitude=4.0)
    print(f'ℹ️ Foram encontrados – {len(df)} – terremotos')
    print(df[['time', 'place', 'magnitude']].head(10).to_string)
    print(f'\n📊 As estatísticas dos terremotos {get_summary_stats(df)}')
