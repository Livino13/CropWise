"""External field data: live weather forecast and modelled soil properties.

Open-Meteo and ISRIC SoilGrids are free and do not need API keys. Every call is
cached in memory and fails soft — a crop plan must still be produced when the
network is unavailable.
"""
import logging
import time
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

_CACHE: dict[str, tuple[float, dict]] = {}
WEATHER_TTL = 60 * 60          # 1 hour
SOIL_TTL = 7 * 24 * 60 * 60    # 7 days
MAX_RAINFALL = 1000.0


def _cached(key: str, ttl: int) -> Optional[dict]:
    item = _CACHE.get(key)
    if item and time.monotonic() - item[0] < ttl:
        return item[1]
    return None


def _store(key: str, value: dict) -> dict:
    _CACHE[key] = (time.monotonic(), value)
    return value


def _mean(values: list[float]) -> Optional[float]:
    clean = [float(v) for v in values if v is not None]
    return sum(clean) / len(clean) if clean else None


def _total(values: list[float]) -> float:
    return sum(float(v) for v in values if v is not None)


async def fetch_weather(latitude: float, longitude: float) -> Optional[dict]:
    """7-day forecast: rain, reference evapotranspiration and temperatures."""
    key = f"weather:{latitude:.4f},{longitude:.4f}"
    hit = _cached(key, WEATHER_TTL)
    if hit is not None:
        return hit

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,et0_fao_evapotranspiration",
        "forecast_days": 7,
        "timezone": "auto",
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://api.open-meteo.com/v1/forecast", params=params)
        if resp.status_code != 200:
            logger.warning("Open-Meteo returned %s", resp.status_code)
            return None
        daily = resp.json().get("daily") or {}
        tmax = daily.get("temperature_2m_max") or []
        tmin = daily.get("temperature_2m_min") or []
        rain = daily.get("precipitation_sum") or []
        et0 = daily.get("et0_fao_evapotranspiration") or []
        if not tmax and not rain:
            return None

        avg = _mean(list(tmax) + list(tmin))
        est_et0 = None
        if not any(v is not None for v in et0) and avg is not None:
            # Conservative fallback when ET0 is missing from the response.
            est_et0 = max(1.5, 0.11 * avg + 0.9) * 7
        value = {
            "rain_7d_mm": round(min(_total(rain), MAX_RAINFALL), 1),
            "et0_7d_mm": round(_total(et0), 1) if any(v is not None for v in et0) else round(est_et0 or 0.0, 1),
            "temp_avg_c": round(avg, 1) if avg is not None else None,
            "temp_max_c": round(max((v for v in tmax if v is not None), default=avg or 0.0), 1),
            "temp_min_c": round(min((v for v in tmin if v is not None), default=avg or 0.0), 1),
            "source": "Open-Meteo 7-day forecast",
        }
        return _store(key, value)
    except Exception as exc:
        logger.warning("Open-Meteo fetch failed: %s", exc)
        return None


async def fetch_soil_properties(latitude: float, longitude: float) -> Optional[dict]:
    """Modelled topsoil properties from ISRIC SoilGrids (250 m grid)."""
    key = f"soil:{latitude:.4f},{longitude:.4f}"
    hit = _cached(key, SOIL_TTL)
    if hit is not None:
        return hit

    params = [
        ("lon", longitude),
        ("lat", latitude),
        ("property", "phh2o"),
        ("property", "clay"),
        ("property", "sand"),
        ("depth", "0-5cm"),
        ("value", "mean"),
    ]
    try:
        async with httpx.AsyncClient(timeout=12) as client:
            resp = await client.get(
                "https://rest.isric.org/soilgrids/v2.0/properties/query", params=params
            )
        if resp.status_code != 200:
            logger.warning("SoilGrids returned %s", resp.status_code)
            return None

        layers = (resp.json().get("properties") or {}).get("layers") or []
        ph = clay = sand = None
        for layer in layers:
            name = layer.get("name")
            depths = layer.get("depths") or []
            if not depths:
                continue
            mean = (depths[0].get("values") or {}).get("mean")
            if mean is None:
                continue
            unit = (layer.get("unit") or "").lower()
            if name == "phh2o":
                ph = round(float(mean) / 10.0, 1)  # pH x 10
            elif name in ("clay", "sand"):
                pct = float(mean) / 10.0 if unit == "g/kg" else float(mean)
                if name == "clay":
                    clay = round(pct, 1)
                else:
                    sand = round(pct, 1)

        if ph is None and clay is None and sand is None:
            return None
        value = {
            "ph": ph,
            "clay_pct": clay,
            "sand_pct": sand,
            "source": "ISRIC SoilGrids (modelled, 0-5 cm)",
        }
        return _store(key, value)
    except Exception as exc:
        logger.warning("SoilGrids fetch failed: %s", exc)
        return None
