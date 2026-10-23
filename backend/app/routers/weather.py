from fastapi import APIRouter
from datetime import datetime
import httpx
from ..schemas.weather import WeatherRequest, WeatherResponse

router = APIRouter(prefix="/api", tags=["weather"])

# SoilInput.rainfall limit — keep weather auto-fill inside the accepted range
MAX_RAINFALL = 1000.0
NORMALS_START_YEAR = datetime.now().year - 11  # ~10 complete years
NORMALS_END_YEAR = datetime.now().year - 1


@router.post("/weather", response_model=WeatherResponse)
async def get_weather(req: WeatherRequest):
    """10-year climate normals from the Open-Meteo archive (avg temp, humidity,
    monthly-average rainfall scaled to mm) instead of a single year's weather."""
    base = {
        "latitude": req.latitude, "longitude": req.longitude,
        "start_date": f"{NORMALS_START_YEAR}-01-01", "end_date": f"{NORMALS_END_YEAR}-12-31",
        "daily": "temperature_2m_mean,precipitation_sum,relativehumidity_2m_mean",
        "timezone": "auto",
    }
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get("https://archive-api.open-meteo.com/v1/archive", params=base)
            if r.status_code != 200:
                # some locations lack daily humidity coverage — retry temp+rain only
                r = await client.get(
                    "https://archive-api.open-meteo.com/v1/archive",
                    params={**base, "daily": "temperature_2m_mean,precipitation_sum"},
                )
            if r.status_code == 200:
                d = r.json().get("daily", {})
                temps = [t for t in d.get("temperature_2m_mean", []) if t is not None]
                rains = [v for v in d.get("precipitation_sum", []) if v is not None]
                hums = [h for h in d.get("relativehumidity_2m_mean", []) if h is not None]
                if temps and rains:
                    humidity = round(sum(hums) / len(hums), 1) if hums else 65.0
                    # daily precip sum averaged over ~10 years of days -> ~monthly normal
                    rainfall = min(round(sum(rains) / len(rains) * 30, 1), MAX_RAINFALL)
                    return WeatherResponse(
                        temperature=round(sum(temps) / len(temps), 1),
                        humidity=humidity,
                        rainfall=rainfall,
                        source=f"open-meteo normals {NORMALS_START_YEAR}-{NORMALS_END_YEAR}",
                    )
    except Exception:
        pass
    # fallback estimate by latitude
    temp = 30 - abs(req.latitude) * 0.5
    return WeatherResponse(temperature=round(temp, 1), humidity=65.0, rainfall=80.0, source="estimate")
