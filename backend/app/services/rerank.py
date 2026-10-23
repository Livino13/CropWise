"""Transparent post-model re-ranking using soil type and planting season.

The RF model never sees soil_type or calendar season (the training dataset has
neither column). Instead of faking model inputs, compatible crops get a small
score boost and incompatible ones a demotion — model confidence is preserved
separately so every adjustment is explainable.
"""
from datetime import date

# soil types accepted by the Field schema
SOIL_TYPES = {"Alluvial", "Black", "Red", "Sandy", "Loamy", "Clayey", "Laterite"}

# which of the 7 soil types each crop grows well in (Indian agronomy, simplified)
CROP_SOIL_PREF = {
    "rice": {"Clayey", "Loamy", "Alluvial"},
    "maize": {"Loamy", "Alluvial"},
    "chickpea": {"Loamy", "Clayey"},
    "kidneybeans": {"Loamy", "Red"},
    "pigeonpeas": {"Red", "Black", "Loamy"},
    "mothbeans": {"Sandy", "Red"},
    "mungbean": {"Sandy", "Loamy", "Red"},
    "blackgram": {"Loamy", "Black"},
    "lentil": {"Loamy", "Clayey"},
    "pomegranate": {"Red", "Sandy", "Loamy"},
    "banana": {"Loamy", "Alluvial"},
    "mango": {"Loamy", "Red", "Laterite"},
    "grapes": {"Sandy", "Loamy", "Red"},
    "watermelon": {"Sandy", "Loamy"},
    "muskmelon": {"Sandy", "Loamy"},
    "apple": {"Loamy", "Red"},
    "orange": {"Loamy", "Laterite", "Red"},
    "papaya": {"Loamy", "Alluvial"},
    "coconut": {"Sandy", "Laterite", "Alluvial"},
    "cotton": {"Black", "Loamy"},
    "jute": {"Loamy", "Alluvial"},
    "coffee": {"Loamy", "Laterite", "Red"},
    "wheat": {"Loamy", "Clayey", "Alluvial"},
    "barley": {"Loamy", "Clayey"},
    "potato": {"Loamy", "Alluvial", "Black"},
    "onion": {"Loamy", "Alluvial"},
    "sorghum": {"Loamy", "Black", "Clayey"},
    "sunflower": {"Loamy", "Black", "Alluvial"},
    "rapeseed": {"Loamy", "Clayey"},
    "ragi": {"Loamy", "Red", "Clayey"},
    "horsegram": {"Loamy", "Red", "Sandy"},
    "turmeric": {"Loamy", "Red", "Laterite"},
    "sweet_potato": {"Sandy", "Loamy", "Red"},
    "soybean": {"Loamy", "Black"},
    "coriander": {"Loamy", "Red"},
    "garlic": {"Loamy", "Red", "Alluvial"},
    "blackpepper": {"Laterite", "Loamy", "Red"},
    "tomato": {"Loamy", "Red", "Alluvial"},
    "brinjal": {"Loamy", "Black", "Alluvial"},
    "cardamom": {"Laterite", "Loamy", "Red"},
    "okra": {"Loamy", "Red", "Black"},
    "pineapple": {"Sandy", "Laterite", "Loamy"},
    "cabbage": {"Loamy", "Clayey"},
    "cauliflower": {"Loamy", "Alluvial"},
    "jackfruit": {"Loamy", "Alluvial", "Red"},
    "drumstick": {"Sandy", "Loamy", "Red"},
    "cucumber": {"Sandy", "Loamy"},
    "radish": {"Loamy", "Sandy"},
    "bottle_gourd": {"Loamy", "Red"},
    "bitter_gourd": {"Loamy", "Alluvial"},
    "pumpkin": {"Loamy", "Sandy", "Red"},
}

# annual planting seasons in India; perennials (empty set) are exempt
CROP_ANNUAL_SEASONS = {
    "rice": {"kharif"}, "maize": {"kharif"}, "chickpea": {"rabi"},
    "kidneybeans": {"kharif"}, "pigeonpeas": {"kharif"}, "mothbeans": {"kharif"},
    "mungbean": {"kharif", "rabi"}, "blackgram": {"kharif"}, "lentil": {"rabi"},
    "watermelon": {"zaid", "kharif"}, "muskmelon": {"zaid", "kharif"},
    "cotton": {"kharif"}, "jute": {"kharif"},
    "wheat": {"rabi"}, "barley": {"rabi"}, "coriander": {"rabi"}, "garlic": {"rabi"},
    "rapeseed": {"rabi"}, "potato": {"rabi"},
    "onion": {"kharif", "rabi"}, "ragi": {"kharif", "rabi"}, "sorghum": {"kharif", "rabi"},
    "horsegram": {"kharif", "rabi"}, "soybean": {"kharif"},
    "sunflower": {"kharif", "rabi", "zaid"}, "tomato": {"kharif", "rabi", "zaid"},
    "okra": {"kharif", "rabi", "zaid"},
    "sweet_potato": {"kharif", "rabi"}, "cabbage": {"kharif", "rabi"},
    "cauliflower": {"kharif", "rabi"}, "cucumber": {"kharif", "rabi"},
    "bottle_gourd": {"kharif", "rabi"}, "bitter_gourd": {"kharif", "rabi"},
    "pumpkin": {"kharif", "rabi"}, "turmeric": {"kharif", "zaid"},
    # perennials: pomegranate, banana, mango, grapes, apple, orange, papaya,
    # coconut, coffee, blackpepper, cardamom, jackfruit, drumstick, pineapple,
    # plus year-round annuals (radish, brinjal) -> no season penalty
}

SOIL_BOOST, SOIL_PENALTY = 1.12, 0.85
SEASON_BOOST, SEASON_PENALTY = 1.10, 0.88


def current_season(today: date | None = None) -> str:
    m = (today or date.today()).month
    if 6 <= m <= 9:
        return "kharif"   # monsoon planting
    if 10 <= m or m <= 3:
        return "rabi"     # winter planting (October is the Rabi sowing window)
    return "zaid"         # summer (Apr-May)


def rerank(crops: list[dict], soil_type: str | None, season: str | None = None) -> tuple[list[dict], list[str]]:
    """Adjust model top-N scores for soil-type fit and planting season.

    Returns (reranked list with model_confidence preserved, human-readable notes).
    Crops keep their model confidence in `model_confidence`; `confidence` becomes
    the adjusted, renormalized score.
    """
    season = season or current_season()
    notes: list[str] = []
    st = soil_type if soil_type in SOIL_TYPES else None

    adjusted: list[dict] = []
    for c in crops:
        crop = c["crop"]
        mc = float(c.get("confidence", 0.0))
        mult = 1.0
        crop_notes: list[str] = []

        if st is not None:
            pref = CROP_SOIL_PREF.get(crop)
            if pref is not None:
                if st in pref:
                    mult *= SOIL_BOOST
                    crop_notes.append(f"{st} soil suits this crop (+)")
                else:
                    mult *= SOIL_PENALTY
                    crop_notes.append(f"prefers {'/'.join(sorted(pref))} soil (-)")

        seasons = CROP_ANNUAL_SEASONS.get(crop)
        if seasons:  # annual crop - season matters; perennials exempt
            if season in seasons:
                mult *= SEASON_BOOST
                crop_notes.append(f"{season.capitalize()} is in-season (+)")
            else:
                mult *= SEASON_PENALTY
                crop_notes.append(f"out of season for {season.capitalize()} (-)")

        adjusted.append({**c, "model_confidence": mc, "confidence": mc * mult, "adjustments": crop_notes})
        for n in crop_notes:
            notes.append(f"{crop}: {n}")

    total = sum(a["confidence"] for a in adjusted)
    if total > 0:
        for a in adjusted:
            a["confidence"] = a["confidence"] / total
    adjusted.sort(key=lambda a: a["confidence"], reverse=True)
    return adjusted, notes
