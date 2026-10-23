"""Structured agronomic profiles used to compute per-field crop plans.

Duration ranges, planting windows and critical stages are standard Indian
package-of-practices values (also summarised in the curated cultivation dataset
under backend/data/raw/cultivation-guide). Water need is relative and used to
scale reference evapotranspiration; it is not a millimetre figure.
"""

# days = (min, max) from planting to first harvest.
# windows = preferred planting months (1-12, inclusive; wrapping is allowed).
# water = low | medium | high relative crop water demand.
# stages = growth stages where water stress hurts yield most.
CROP_PROFILES = {
    "rice": {"days": (120, 150), "windows": [(6, 7), (10, 11)], "water": "high", "stages": ["tillering", "panicle initiation", "flowering"]},
    "maize": {"days": (90, 110), "windows": [(6, 7), (10, 11), (2, 3)], "water": "medium", "stages": ["knee-high", "tasseling", "grain filling"]},
    "chickpea": {"days": (95, 105), "windows": [(10, 11)], "water": "low", "stages": ["flowering", "pod filling"]},
    "kidneybeans": {"days": (100, 140), "windows": [(10, 11), (2, 3)], "water": "medium", "stages": ["flowering", "pod filling"]},
    "pigeonpeas": {"days": (150, 180), "windows": [(6, 7)], "water": "low", "stages": ["flowering", "pod filling"]},
    "mothbeans": {"days": (75, 90), "windows": [(7, 8)], "water": "low", "stages": ["flowering", "pod filling"]},
    "mungbean": {"days": (60, 70), "windows": [(7, 7), (10, 10), (2, 3)], "water": "low", "stages": ["flowering", "pod filling"]},
    "blackgram": {"days": (70, 80), "windows": [(7, 7), (10, 10)], "water": "medium", "stages": ["flowering", "pod filling"]},
    "lentil": {"days": (110, 130), "windows": [(10, 11)], "water": "low", "stages": ["flowering", "pod filling"]},
    "pomegranate": {"days": (550, 730), "windows": [(2, 3), (7, 8)], "water": "medium", "stages": ["flowering", "fruit development"], "perennial": True},
    "banana": {"days": (330, 450), "windows": [(2, 3), (9, 10)], "water": "high", "stages": ["vegetative growth", "bunch development"], "perennial": True},
    "mango": {"days": (1095, 1825), "windows": [(2, 3), (8, 9)], "water": "medium", "stages": ["flowering", "fruit set"], "perennial": True},
    "grapes": {"days": (730, 730), "windows": [(1, 2)], "water": "medium", "stages": ["flowering", "berry development"], "perennial": True},
    "watermelon": {"days": (70, 100), "windows": [(11, 12), (1, 2)], "water": "medium", "stages": ["flowering", "fruit filling"]},
    "muskmelon": {"days": (70, 90), "windows": [(11, 1), (2, 3)], "water": "medium", "stages": ["flowering", "fruit filling"]},
    "apple": {"days": (1460, 1460), "windows": [(1, 2)], "water": "medium", "stages": ["fruit set", "fruit development"], "perennial": True},
    "orange": {"days": (1095, 1095), "windows": [(7, 8)], "water": "medium", "stages": ["flowering", "fruit set"], "perennial": True},
    "papaya": {"days": (270, 300), "windows": [(2, 3), (9, 10)], "water": "medium", "stages": ["establishment", "flowering"], "perennial": True},
    "coconut": {"days": (2190, 2190), "windows": [(6, 7)], "water": "high", "stages": ["inflorescence", "nut development"], "perennial": True},
    "cotton": {"days": (150, 180), "windows": [(5, 6)], "water": "medium", "stages": ["flowering", "boll formation"]},
    "jute": {"days": (120, 150), "windows": [(3, 5)], "water": "high", "stages": ["germination", "fibre growth"]},
    "coffee": {"days": (1095, 1460), "windows": [(6, 7)], "water": "high", "stages": ["flowering", "fruit development"], "perennial": True},
    "barley": {"days": (110, 140), "windows": [(10, 11)], "water": "low", "stages": ["tillering", "heading", "grain filling"]},
    "bitter_gourd": {"days": (55, 70), "windows": [(2, 3), (6, 7)], "water": "medium", "stages": ["flowering", "fruiting"]},
    "blackpepper": {"days": (1095, 1460), "windows": [(6, 7)], "water": "high", "stages": ["flowering", "berry development"], "perennial": True},
    "bottle_gourd": {"days": (60, 75), "windows": [(1, 3), (6, 7)], "water": "medium", "stages": ["flowering", "fruit development"]},
    "brinjal": {"days": (120, 140), "windows": [(6, 7), (10, 11)], "water": "medium", "stages": ["flowering", "fruit development"]},
    "cabbage": {"days": (70, 120), "windows": [(9, 11), (3, 5)], "water": "medium", "stages": ["head formation"]},
    "cardamom": {"days": (730, 1095), "windows": [(6, 7)], "water": "high", "stages": ["flowering", "capsule filling"], "perennial": True},
    "cauliflower": {"days": (60, 120), "windows": [(9, 11), (3, 4)], "water": "medium", "stages": ["curd formation"]},
    "coriander": {"days": (90, 110), "windows": [(10, 11)], "water": "low", "stages": ["flowering", "seed filling"]},
    "cucumber": {"days": (50, 70), "windows": [(2, 3), (6, 7)], "water": "medium", "stages": ["flowering", "fruit development"]},
    "drumstick": {"days": (180, 240), "windows": [(6, 7)], "water": "low", "stages": ["flowering", "pod development"], "perennial": True},
    "garlic": {"days": (150, 180), "windows": [(10, 11)], "water": "low", "stages": ["bulb formation"]},
    "horsegram": {"days": (120, 180), "windows": [(6, 7), (9, 10)], "water": "low", "stages": ["flowering", "pod filling"]},
    "jackfruit": {"days": (1095, 2920), "windows": [(6, 7)], "water": "medium", "stages": ["flowering", "fruit development"], "perennial": True},
    "okra": {"days": (50, 60), "windows": [(2, 3), (6, 7)], "water": "medium", "stages": ["flowering", "pod development"]},
    "onion": {"days": (120, 150), "windows": [(6, 7), (10, 12)], "water": "medium", "stages": ["bulb formation"]},
    "pineapple": {"days": (540, 730), "windows": [(5, 7)], "water": "medium", "stages": ["vegetative growth", "fruit development"], "perennial": True},
    "potato": {"days": (90, 120), "windows": [(10, 11), (1, 2)], "water": "medium", "stages": ["tuber initiation", "tuber bulking"]},
    "pumpkin": {"days": (90, 120), "windows": [(2, 4), (6, 7)], "water": "medium", "stages": ["flowering", "fruit development"]},
    "radish": {"days": (30, 60), "windows": [(9, 2)], "water": "low", "stages": ["root development"]},
    "ragi": {"days": (110, 140), "windows": [(6, 7), (9, 10)], "water": "low", "stages": ["tillering", "grain filling"]},
    "rapeseed": {"days": (120, 140), "windows": [(10, 11)], "water": "medium", "stages": ["flowering", "pod filling"]},
    "sorghum": {"days": (100, 140), "windows": [(6, 7), (9, 10)], "water": "low", "stages": ["flowering", "grain filling"]},
    "soybean": {"days": (90, 110), "windows": [(6, 7)], "water": "medium", "stages": ["flowering", "pod filling"]},
    "sunflower": {"days": (90, 120), "windows": [(6, 7), (10, 11), (1, 2)], "water": "medium", "stages": ["flowering", "seed filling"]},
    "sweet_potato": {"days": (90, 120), "windows": [(2, 3), (7, 8)], "water": "medium", "stages": ["tuber initiation", "tuber bulking"]},
    "tomato": {"days": (120, 140), "windows": [(6, 7), (10, 11), (1, 2)], "water": "medium", "stages": ["flowering", "fruit set"]},
    "turmeric": {"days": (210, 300), "windows": [(5, 6)], "water": "high", "stages": ["rhizome development"]},
    "wheat": {"days": (120, 150), "windows": [(11, 11)], "water": "medium", "stages": ["crown root", "heading", "grain filling"]},
}

DEFAULT_PROFILE = {
    "days": (90, 150),
    "windows": [],
    "water": "medium",
    "stages": ["flowering", "grain or fruit filling"],
}

WATER_KC = {"low": 0.65, "medium": 0.85, "high": 1.10}

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def get_profile(crop: str) -> dict:
    return CROP_PROFILES.get(crop, DEFAULT_PROFILE)


def month_name(month: int) -> str:
    return MONTHS[(month - 1) % 12]


def in_window(month: int, start: int, end: int) -> bool:
    if start <= end:
        return start <= month <= end
    return month >= start or month <= end


def current_season(month: int) -> str:
    """Align with the app's crop calendar: October starts the Rabi season."""
    if 6 <= month <= 9:
        return "Kharif"
    if month >= 10 or month <= 3:
        return "Rabi"
    return "Zaid"
