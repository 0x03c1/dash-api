import pandas as pd
import requests
from datetime import datetime, timezone, timedelta

def fetch_earthquake(
        dias_atras: int = 7,
        magnitude_minima: float = 2.0
    ) -> pd.DataFrame:
        
        endtime = datetime.now(timezone.utc)
        starttime = endtime - timedelta(days=dias_atras)

        param = {
                "format": "geojson",
                "place": "",
                "starttime": starttime.strftime("%Y-%m-%dT%H:%M:%S"),
                "endtime": endtime.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        
