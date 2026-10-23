"""Compute a per-field crop plan from agronomic profiles and field data.

This module is deliberately deterministic: every number is calculated from the
reference targets, the farmer's soil values and the weather data supplied by the
caller. The LLM layer may explain the result, but never creates the numbers.
"""
import re
from datetime import date, timedelta
from typing import Optional

from .agronomy import CROP_NPK_TARGET, DOSE_UNIT, FERTILIZER_STAGES, PEST_GUIDE
from .crop_profiles import (
    WATER_KC,
    current_season,
    get_profile,
    in_window,
    month_name,
)

HA_PER_ACRE = 2.47105
BAG_KG = 50.0

_FRACTION_RE = re.compile(r"(\d+)\s*%|(\d+)\s*/\s*(\d+)")

# Crops harvested repeatedly (first date is the start of picking, not the end).
_MULTI_PICK = {
    "tomato", "brinjal", "okra", "cucumber", "bitter_gourd", "bottle_gourd",
    "pumpkin", "beans", "kidneybeans", "pigeonpeas",
}

_SOIL_INTERVAL_DAYS = {
    "sandy": 3,
    "red": 4,
    "laterite": 5,
    "loamy": 5,
    "alluvial": 5,
    "black": 7,
    "clayey": 8,
}


def _num(value) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _field_attr(field, name):
    return getattr(field, name, None) if field is not None else None


def _resolve_soil(field, inputs: dict, soil_est: Optional[dict]) -> dict:
    """Priority: explicit request values > field soil test > SoilGrids estimate."""
    soil: dict = {"source": "standard targets", "has_test": False, "from_soilgrids": False}

    for key, field_attr, out_key in (
        ("N", "soil_n", "n"),
        ("P", "soil_p", "p"),
        ("K", "soil_k", "k"),
    ):
        explicit = _num(inputs.get(key))
        stored = _num(_field_attr(field, field_attr))
        soil[out_key] = explicit if explicit is not None else stored

    explicit_ph = _num(inputs.get("ph"))
    stored_ph = _num(_field_attr(field, "soil_ph"))
    soilgrid_ph = _num((soil_est or {}).get("ph"))
    soil["ph"] = explicit_ph if explicit_ph is not None else (stored_ph if stored_ph is not None else soilgrid_ph)
    if explicit_ph is None and stored_ph is None and soilgrid_ph is not None:
        soil["from_soilgrids"] = True

    soil["type"] = (inputs.get("soil_type") or _field_attr(field, "soil_type") or "").strip() or None
    soil["has_test"] = any(soil.get(k) is not None for k in ("n", "p", "k"))
    if soil["has_test"]:
        explicit_npk = any(inputs.get(k) is not None for k in ("N", "P", "K"))
        soil["source"] = "your soil values" if explicit_npk else "field soil test"
    return soil


def _next_window(today: date, windows: list[tuple[int, int]]) -> Optional[date]:
    for offset in range(0, 12):
        index = today.month - 1 + offset
        month = index % 12 + 1
        year = today.year + index // 12
        for start, _end in windows:
            if month == start:
                return date(year, month, 1)
    return None


def _sowing_text(profile: dict, today: date, weather: Optional[dict], inputs: dict) -> tuple[str, date, bool]:
    windows = profile.get("windows") or []
    active = any(in_window(today.month, a, b) for a, b in windows)
    season = current_season(today.month)
    perennial = bool(profile.get("perennial"))

    if active:
        start = today
        window = next((w for w in windows if in_window(today.month, *w)), None)
        if window:
            label = f"{month_name(window[0])}–{month_name(window[1])}" if window[0] != window[1] else month_name(window[0])
        else:
            label = season
        text = (
            f"Plant now — the {'main ' if perennial else ''}planting window is {label}."
            if perennial
            else f"Sow now — the planting window is {label} ({season})."
        )
    elif windows:
        start = _next_window(today, windows) or today
        weeks = max(1, round((start - today).days / 7))
        window = next((w for w in windows if w[0] == start.month), windows[0])
        label = f"{month_name(window[0])}–{month_name(window[1])}" if window[0] != window[1] else month_name(window[0])
        text = f"Wait for the next planting window: {label} (about {weeks} weeks away)."
    else:
        start = today
        text = "Year-round planting is possible where reliable water is available."

    tmax = _num((weather or {}).get("temp_max_c"))
    if tmax is None:
        tmax = _num(inputs.get("temperature"))
    tmin = _num((weather or {}).get("temp_min_c"))
    if tmax is not None and tmax >= 38:
        text += " Very hot weather right now — wait for cooler days or shade the nursery and irrigate at establishment."
    if tmin is not None and tmin <= 4:
        text += " Frost risk — protect young plants or delay planting."

    rainfall = _num(inputs.get("rainfall"))
    if rainfall is not None and rainfall < 50 and profile.get("water") == "high" and weather is None:
        text += " Rainfall in your inputs is low for this crop; plan irrigation from day one."

    return text, start, active


def _fmt_date(value: date) -> str:
    return f"{value.day} {month_name(value.month)} {value.year}"


def _harvest_text(profile: dict, start: date, is_planting_now: bool) -> str:
    dmin, dmax = profile["days"]
    first = start + timedelta(days=dmin)
    last = start + timedelta(days=dmax)
    prefix = "" if is_planting_now else "After planting in the next window, "
    perennial = bool(profile.get("perennial"))

    if perennial and dmax >= 365:
        if dmax >= 730:
            lo, hi = round(dmin / 365, 1), round(dmax / 365, 1)
            span = f"{lo:g}–{hi:g} years"
        else:
            lo, hi = round(dmin / 30), round(dmax / 30)
            span = f"{lo}–{hi} months"
        text = (
            f"{prefix}first harvest in about {span} (around {_fmt_date(first)} to {_fmt_date(last)}); "
            "after that, harvests continue seasonally."
        )
    else:
        text = f"{prefix}harvest around {_fmt_date(first)} to {_fmt_date(last)} ({dmin}–{dmax} days after sowing)."

    return text[0].upper() + text[1:] if text else text


def _irrigation_interval(soil_type: Optional[str], water: str) -> int:
    base = 5
    if soil_type:
        key = soil_type.strip().lower()
        for name, days in _SOIL_INTERVAL_DAYS.items():
            if name in key:
                base = days
                break
    if water == "high":
        base -= 1
    elif water == "low":
        base += 1
    return max(3, min(10, base))


def _irrigation_text(
    profile: dict,
    soil_type: Optional[str],
    weather: Optional[dict],
    inputs: dict,
    planting_now: bool,
) -> str:
    stages = ", ".join(profile.get("stages") or ["flowering"])
    water = profile.get("water", "medium")
    interval = _irrigation_interval(soil_type, water)
    kc = WATER_KC.get(water, 0.85)
    perennial = bool(profile.get("perennial"))

    if not planting_now and not perennial:
        after = (
            f"After sowing, this crop has {water} water need: irrigate about every {interval} days, "
            f"especially at {stages}."
        )
        if weather:
            et0 = _num(weather.get("et0_7d_mm")) or 0.0
            rain = _num(weather.get("rain_7d_mm")) or 0.0
            return (
                f"The crop is not in the field yet. This week's forecast (rain ≈{rain:.0f} mm, "
                f"reference ET0 ≈{et0:.0f} mm) is useful for land preparation. {after}"
            )
        return f"The crop is not in the field yet. {after}"

    if weather:
        et0 = _num(weather.get("et0_7d_mm")) or 0.0
        rain = _num(weather.get("rain_7d_mm")) or 0.0
        crop_use = et0 * kc
        net = max(0.0, crop_use - rain * 0.8)
        text = f"Next 7 days: crop water use is about {crop_use:.0f} mm; forecast rain is about {rain:.0f} mm."
        if net >= 5:
            per_event = net / max(1, round(7 / interval))
            if rain < 1:
                text += (
                    f" No rain is forecast, so apply about {net:.0f} mm this week "
                    f"(≈{per_event:.0f} mm per irrigation, about every {interval} days)."
                )
            else:
                text += (
                    f" If that rain does not arrive, apply about {net:.0f} mm this week "
                    f"(≈{per_event:.0f} mm per irrigation, about every {interval} days)."
                )
        else:
            text += " Forecast rain should cover most of the need — check the soil before watering."
        text += f" Most sensitive stages: {stages}."
        return text

    rainfall = _num(inputs.get("rainfall"))
    if rainfall is None:
        return (
            f"This crop has {water} water need. Irrigate about every {interval} days, "
            f"especially at {stages}; adjust to local rain."
        )
    if rainfall < 50:
        return (
            f"Your rainfall input is low (~{rainfall:g} mm). With {water} water need, plan irrigation "
            f"about every {interval} days, especially at {stages}."
        )
    if rainfall <= 150:
        return (
            f"Seasonal rainfall (~{rainfall:g} mm) covers only part of this crop's need. "
            f"Supplement irrigation about every {interval} days, especially at {stages}."
        )
    if water == "high":
        return (
            f"Seasonal rainfall (~{rainfall:g} mm) is substantial and suits this high-water crop. "
            f"Maintain soil moisture at {stages}; drain the field only if it floods."
        )
    return (
        f"Seasonal rainfall (~{rainfall:g} mm) is substantial. Ensure drainage and irrigate only when the soil dries; "
        f"watch {stages}."
    )


def _soil_prep_text(soil: dict, weather: Optional[dict], soil_est: Optional[dict]) -> str:
    soil_type = (soil.get("type") or "").lower()
    parts: list[str] = []

    if "clay" in soil_type or "black" in soil_type:
        parts.append("Make broad beds and keep drainage channels open; avoid tillage when the soil is wet.")
    elif "sand" in soil_type:
        parts.append("Add 5–10 t/ha farmyard manure or compost to improve water holding.")
    elif "red" in soil_type or "laterite" in soil_type:
        parts.append("Incorporate organic matter; use raised beds if drainage is poor.")
    elif "alluvial" in soil_type:
        parts.append("Prepare a fine, level seedbed; alluvial soil usually has good fertility.")
    elif "loam" in soil_type:
        parts.append("Prepare a fine, well-drained seedbed and add 5–10 t/ha farmyard manure.")
    else:
        parts.append("Prepare a fine, weed-free seedbed and add well-rotted farmyard manure.")

    ph = _num(soil.get("ph"))
    if ph is not None:
        if soil.get("from_soilgrids"):
            parts.append(
                f"Modelled topsoil pH is about {ph:g} — confirm with a soil test before applying lime or gypsum."
            )
        elif ph < 5.5:
            parts.append(f"Soil pH {ph:g} is acidic — apply agricultural lime 1–2 t/ha 3–4 weeks before planting.")
        elif ph > 8.0:
            parts.append(f"Soil pH {ph:g} is alkaline — apply gypsum 2–4 t/ha and incorporate organic matter.")
        elif ph > 7.5:
            parts.append(f"Soil pH {ph:g} is slightly alkaline — add organic matter and watch phosphorus availability.")
        elif ph < 6.0:
            parts.append(f"Soil pH {ph:g} is slightly acidic — usually fine, but lime if it drops below 5.5.")
        else:
            parts.append(f"Soil pH {ph:g} is in a good range for most crops.")
    elif soil_est and soil_est.get("ph") is not None:
        parts.append(f"Modelled topsoil pH is about {soil_est['ph']:g}; confirm it with a soil test.")

    rain = _num((weather or {}).get("rain_7d_mm"))
    if rain is not None and rain > 40:
        parts.append("Heavy rain is forecast — finish land preparation early and check drainage.")
    return " ".join(parts)


def _risks(profile: dict, soil: dict, weather: Optional[dict], inputs: dict) -> list[str]:
    risks: list[str] = []
    ph = _num(soil.get("ph"))
    if ph is not None and ph < 5.5:
        risks.append("Acidic soil can lock up phosphorus; lime before planting.")
    elif ph is not None and ph > 8.0:
        risks.append("Alkaline soil can reduce nutrient uptake, especially phosphorus and zinc.")
    rain = _num((weather or {}).get("rain_7d_mm"))
    if rain is not None and rain > 50:
        risks.append("Heavy rain may leach nitrogen; split nitrogen applications.")
    tmax = _num((weather or {}).get("temp_max_c")) or _num(inputs.get("temperature"))
    if tmax is not None and tmax >= 38:
        risks.append("Heat stress risk — irrigate at establishment and avoid midday spraying.")
    tmin = _num((weather or {}).get("temp_min_c"))
    if tmin is not None and tmin <= 4:
        risks.append("Frost risk — protect young plants or delay planting.")
    if rain is not None and rain < 5 and profile.get("water") == "high":
        risks.append("Dry week forecast for a high-water crop — check irrigation daily.")
    if not soil.get("has_test"):
        risks.append("No soil N/P/K values — fertilizer is a standard crop target, not a field-specific deficit.")
    return risks


def _n_fraction(share: str, remaining: float) -> Optional[float]:
    text = share.lower()
    if "remaining" in text:
        return remaining
    match = _FRACTION_RE.search(text)
    if match:
        if match.group(1):
            return min(1.0, int(match.group(1)) / 100.0)
        if match.group(2) and match.group(3):
            return min(1.0, int(match.group(2)) / int(match.group(3)))
    if "half" in text:
        return 0.5
    if "third" in text:
        return 1 / 3
    if "quarter" in text:
        return 0.25
    if "full" in text:
        return 1.0
    return None


def _product(name: str, kg_ha: float) -> dict:
    kg_ha = round(max(0.0, kg_ha), 1)
    kg_acre = round(kg_ha / HA_PER_ACRE, 1)
    return {
        "name": name,
        "kg_per_ha": kg_ha,
        "kg_per_acre": kg_acre,
        "bags_per_acre": round(kg_acre / BAG_KG, 2),
    }


def _fertilizer_plan(crop: str, soil: dict, profile: dict, weather: Optional[dict]) -> dict:
    target = CROP_NPK_TARGET.get(crop)
    unit = DOSE_UNIT.get(crop, "kg/ha")
    stages_raw = FERTILIZER_STAGES.get(crop, [])
    notes: list[str] = []
    ph = _num(soil.get("ph"))

    ph_advice = None
    if ph is not None:
        prefix = "Modelled topsoil pH" if soil.get("from_soilgrids") else "Soil pH"
        suffix = " Confirm with a soil test before amending." if soil.get("from_soilgrids") else ""
        if ph < 5.5:
            ph_advice = f"{prefix} {ph:g} is acidic — apply lime 1–2 t/ha and re-test before the season.{suffix}"
        elif ph > 8.0:
            ph_advice = f"{prefix} {ph:g} is alkaline — apply gypsum 2–4 t/ha or sulphur 100–200 kg/ha.{suffix}"
        elif ph > 7.5:
            ph_advice = f"{prefix} {ph:g} is slightly alkaline — add organic matter and watch phosphorus availability.{suffix}"
        elif ph < 6.0:
            ph_advice = f"{prefix} {ph:g} is slightly acidic — usually fine for most crops.{suffix}"
        else:
            ph_advice = f"{prefix} {ph:g} is in a good range for nutrient availability.{suffix}"

    available = None
    deficit = None
    personalized = False
    products: list[dict] = []
    stages: list[dict] = []

    can_calculate = target is not None and unit == "kg/ha"

    if can_calculate:
        if soil.get("has_test"):
            available = {
                "n": round(soil.get("n") or 0.0, 1),
                "p": round(soil.get("p") or 0.0, 1),
                "k": round(soil.get("k") or 0.0, 1),
            }
            deficit = {
                "n": round(max(0.0, target["n"] - available["n"]), 1),
                "p": round(max(0.0, target["p"] - available["p"]), 1),
                "k": round(max(0.0, target["k"] - available["k"]), 1),
            }
            personalized = True
            dose = deficit
            missing = [label for label, key in (("N", "n"), ("P", "p"), ("K", "k")) if soil.get(key) is None]
            if missing:
                notes.append(f"Missing {'/'.join(missing)} was treated as 0 — a complete soil test gives a better deficit.")
            notes.append("Deficit = the crop's reference target minus your soil values.")
        else:
            dose = {"n": target["n"], "p": target["p"], "k": target["k"]}
            notes.append(
                "Standard crop dose — not adjusted to your soil. "
                "Add soil N/P/K values to get a field-specific deficit."
            )

        # Standard products: DAP (18-46-0), urea (46-0-0), MOP (0-0-60).
        dap = dose["p"] / 0.46
        n_from_dap = dap * 0.18
        urea = max(0.0, dose["n"] - n_from_dap) / 0.46
        mop = dose["k"] / 0.60
        if dap > 0:
            products.append(_product("DAP (18-46-0)", dap))
        if urea > 0:
            products.append(_product("Urea (46-0-0)", urea))
        if mop > 0:
            products.append(_product("MOP (0-0-60)", mop))
        if products:
            notes.append(
                "Product amounts use standard DAP, urea and MOP grades, assuming P and K targets are P₂O₅ and K₂O. "
                "Confirm the grades with your dealer."
            )
            if personalized:
                if deficit["p"] <= 0:
                    notes.append("Your soil already meets the crop's P target, so no DAP is included.")
                if deficit["k"] <= 0:
                    notes.append("Your soil already meets the crop's K target, so no MOP is included.")
                if deficit["n"] <= 0:
                    notes.append("Your soil already meets the crop's N target, so no urea is included.")
                elif urea <= 0 and dap > 0:
                    notes.append("DAP supplies enough nitrogen to cover the calculated N deficit, so no urea is included.")
        elif personalized:
            notes.append("Your soil already meets the crop's N, P and K targets — no fertilizer deficit calculated.")
    else:
        notes.append("This crop is dosed per plant, tree or vine, so the per-hectare deficit calculation does not apply.")

    # Stage schedule. P and K are assumed basal; nitrogen follows the reference shares.
    remaining = 1.0
    parsed: list[Optional[float]] = []
    for stage in stages_raw:
        frac = _n_fraction(stage.get("share", ""), remaining)
        parsed.append(frac)
        if frac is not None:
            remaining = max(0.0, remaining - frac)

    total_urea = next((p["kg_per_ha"] for p in products if p["name"].startswith("Urea")), 0.0)
    total_dap = next((p["kg_per_ha"] for p in products if p["name"].startswith("DAP")), 0.0)
    total_mop = next((p["kg_per_ha"] for p in products if p["name"].startswith("MOP")), 0.0)

    for index, stage in enumerate(stages_raw):
        frac = parsed[index]
        urea_stage = round(total_urea * frac, 1) if frac is not None and can_calculate else None
        dap_stage = round(total_dap, 1) if index == 0 and can_calculate and total_dap > 0 else None
        mop_stage = round(total_mop, 1) if index == 0 and can_calculate and total_mop > 0 else None
        stages.append({
            "stage": stage.get("stage", ""),
            "share": stage.get("share", ""),
            "products": stage.get("products", ""),
            "urea_kg": urea_stage,
            "dap_kg": dap_stage,
            "mop_kg": mop_stage,
        })

    if can_calculate and remaining > 0.05:
        notes.append("Part of the nitrogen dose was not assigned a stage by the reference schedule; adjust with local advice.")

    rain = _num((weather or {}).get("rain_7d_mm"))
    soil_type = (soil.get("type") or "").lower()
    if "sand" in soil_type or (rain is not None and rain > 30):
        notes.append("Split nitrogen into 2–3 doses and avoid applying it just before heavy rain — sandy soil and wet weather leach nitrogen.")

    return {
        "unit": unit,
        "target": {"n": target["n"], "p": target["p"], "k": target["k"]} if target else None,
        "available": available,
        "deficit": deficit,
        "products": products,
        "stages": stages,
        "personalized": personalized,
        "ph_advice": ph_advice,
        "notes": notes,
    }


def build_crop_plan(
    crop: str,
    *,
    field=None,
    inputs: Optional[dict] = None,
    weather: Optional[dict] = None,
    soil_est: Optional[dict] = None,
    today: Optional[date] = None,
) -> dict:
    """Build a computed growing + fertilizer plan for one crop."""
    inputs = inputs or {}
    today = today or date.today()
    profile = get_profile(crop)
    soil = _resolve_soil(field, inputs, soil_est)

    sowing, sow_start, planting_now = _sowing_text(profile, today, weather, inputs)
    harvest = _harvest_text(profile, sow_start, planting_now)
    irrigation = _irrigation_text(
        profile, soil.get("type"), weather, inputs, planting_now
    )
    soil_prep = _soil_prep_text(soil, weather, soil_est)

    weather_source = (weather or {}).get("source")
    if weather_source is None and any(inputs.get(k) is not None for k in ("temperature", "humidity", "rainfall")):
        weather_source = "Saved climate inputs"
    soil_source = soil.get("source")
    if soil.get("from_soilgrids"):
        if soil.get("has_test"):
            soil_source = f"{soil.get('source') or 'your soil values'} for N/P/K; SoilGrids for pH"
        else:
            soil_source = (soil_est or {}).get("source") or "SoilGrids estimate"

    basis_notes: list[str] = []
    if weather:
        basis_notes.append("Uses a 7-day weather forecast for the selected field.")
    elif weather_source:
        basis_notes.append("Uses the climate values you entered.")
    else:
        basis_notes.append("Uses reference practices and the current planting calendar.")
    if soil.get("has_test"):
        basis_notes.append("Fertilizer is calculated from your soil N/P/K values.")
    else:
        basis_notes.append("Fertilizer is a standard crop dose, not a soil-test deficit.")
    if soil.get("from_soilgrids"):
        basis_notes.append("Soil pH is a modelled SoilGrids estimate — confirm it with a soil test.")
    if not soil.get("has_test"):
        basis_notes.append("Add soil N/P/K values for a field-specific fertilizer deficit.")

    personalized = bool(soil.get("has_test") or weather or weather_source)
    return {
        "crop": crop,
        "field": (
            {"id": _field_attr(field, "id"), "name": _field_attr(field, "name")}
            if field is not None
            else None
        ),
        "personalized": personalized,
        "basis": {
            "weather": weather_source,
            "soil": soil_source,
            "personalized": personalized,
            "notes": basis_notes,
        },
        "growing": {
            "sowing": sowing,
            "harvest": harvest,
            "irrigation": irrigation,
            "soil_prep": soil_prep,
            "risks": _risks(profile, soil, weather, inputs),
        },
        "fertilizer": _fertilizer_plan(crop, soil, profile, weather),
        "pests": PEST_GUIDE.get(crop, [])[:4],
    }
