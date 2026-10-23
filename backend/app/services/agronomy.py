"""Agronomy knowledge base: fertilizer schedules and pest guidance for all 51 crops.

Curated once from the Comprehensive Crop Cultivation Dataset (Kaggle:
sashankgarg23/comprehensive-crop-cultivation-dataset, Apache-2.0) and standard
Indian agronomy references. NPK targets are season totals in kg/ha (midpoint of
the source range); per-plant/per-vine crops carry a unit and skip deficit math.
"""

CROP_NPK_TARGET = {
    "apple": None,
    "banana": None,
    "barley": {'n': 70.0, 'p': 45.0, 'k': 35.0},
    "bitter_gourd": {'n': 70.0, 'p': 45.0, 'k': 45.0},
    "blackgram": {'n': 22.5, 'p': 45.0, 'k': 22.5},
    "blackpepper": None,
    "bottle_gourd": {'n': 70.0, 'p': 55.0, 'k': 55.0},
    "brinjal": {'n': 125.0, 'p': 62.5, 'k': 62.5},
    "cabbage": {'n': 135.0, 'p': 70.0, 'k': 90.0},
    "cardamom": {'n': 97.5, 'p': 97.5, 'k': 195.0},
    "cauliflower": {'n': 135.0, 'p': 70.0, 'k': 70.0},
    "chickpea": {'n': 25.0, 'p': 50.0, 'k': 23.5},
    "coconut": None,
    "coffee": None,
    "coriander": {'n': 50.0, 'p': 35.0, 'k': 25.0},
    "cotton": {'n': 135.0, 'p': 67.5, 'k': 67.5},
    "cucumber": {'n': 70.0, 'p': 55.0, 'k': 55.0},
    "drumstick": None,
    "garlic": {'n': 70.0, 'p': 55.0, 'k': 45.0},
    "grapes": None,
    "horsegram": {'n': 25.0, 'p': 50.0, 'k': 12.5},
    "jackfruit": None,
    "jute": {'n': 60.0, 'p': 20.0, 'k': 20.0},
    "kidneybeans": {'n': 22.5, 'p': 45.0, 'k': 25.0},
    "lentil": {'n': 17.5, 'p': 45.0, 'k': 20.0},
    "maize": {'n': 150.0, 'p': 75.0, 'k': 75.0},
    "mango": None,
    "mothbeans": {'n': 17.5, 'p': 35.0, 'k': 17.5},
    "mungbean": {'n': 17.5, 'p': 35.0, 'k': 20.0},
    "muskmelon": {'n': 55.0, 'p': 45.0, 'k': 55.0},
    "okra": {'n': 70.0, 'p': 45.0, 'k': 45.0},
    "onion": {'n': 110.0, 'p': 55.0, 'k': 70.0},
    "orange": None,
    "papaya": None,
    "pigeonpeas": {'n': 27.5, 'p': 45.0, 'k': 30.0},
    "pineapple": None,
    "pomegranate": None,
    "potato": {'n': 135.0, 'p': 70.0, 'k': 110.0},
    "pumpkin": {'n': 70.0, 'p': 55.0, 'k': 70.0},
    "radish": {'n': 70.0, 'p': 45.0, 'k': 45.0},
    "ragi": {'n': 62.5, 'p': 45.0, 'k': 31.2},
    "rapeseed": {'n': 100.0, 'p': 50.0, 'k': 40.0},
    "rice": {'n': 120.0, 'p': 60.0, 'k': 40.0},
    "sorghum": {'n': 90.0, 'p': 45.0, 'k': 40.0},
    "soybean": {'n': 25.0, 'p': 70.0, 'k': 35.0},
    "sunflower": {'n': 70.0, 'p': 70.0, 'k': 50.0},
    "sweet_potato": {'n': 55.0, 'p': 55.0, 'k': 90.0},
    "tomato": {'n': 135.0, 'p': 90.0, 'k': 90.0},
    "turmeric": {'n': 60.0, 'p': 50.0, 'k': 120.0},
    "watermelon": {'n': 57.5, 'p': 57.5, 'k': 57.5},
    "wheat": {'n': 135.0, 'p': 60.0, 'k': 40.0},
}

DOSE_UNIT = {
    "apple": "per tree/year",
    "banana": "per plant",
    "barley": "kg/ha",
    "bitter_gourd": "kg/ha",
    "blackgram": "kg/ha",
    "blackpepper": "per vine/year",
    "bottle_gourd": "kg/ha",
    "brinjal": "kg/ha",
    "cabbage": "kg/ha",
    "cardamom": "kg/ha",
    "cauliflower": "kg/ha",
    "chickpea": "kg/ha",
    "coconut": "per palm/year",
    "coffee": "per plant/year",
    "coriander": "kg/ha",
    "cotton": "kg/ha",
    "cucumber": "kg/ha",
    "drumstick": "per tree",
    "garlic": "kg/ha",
    "grapes": "per vine/crop",
    "horsegram": "kg/ha",
    "jackfruit": "per tree/year",
    "jute": "kg/ha",
    "kidneybeans": "kg/ha",
    "lentil": "kg/ha",
    "maize": "kg/ha",
    "mango": "per tree/year",
    "mothbeans": "kg/ha",
    "mungbean": "kg/ha",
    "muskmelon": "kg/ha",
    "okra": "kg/ha",
    "onion": "kg/ha",
    "orange": "per tree/year",
    "papaya": "per plant/year",
    "pigeonpeas": "kg/ha",
    "pineapple": "per plant/year",
    "pomegranate": "per plant/year",
    "potato": "kg/ha",
    "pumpkin": "kg/ha",
    "radish": "kg/ha",
    "ragi": "kg/ha",
    "rapeseed": "kg/ha",
    "rice": "kg/ha",
    "sorghum": "kg/ha",
    "soybean": "kg/ha",
    "sunflower": "kg/ha",
    "sweet_potato": "kg/ha",
    "tomato": "kg/ha",
    "turmeric": "kg/ha",
    "watermelon": "kg/ha",
    "wheat": "kg/ha",
}

FERTILIZER_STAGES = {
    "apple": [
        {"stage": 'Splits through season', "share": 'Divide season dose', "products": 'NPK per tree + 30-50 kg FYM (bearing)'},
    ],
    "banana": [
        {"stage": '3rd month', "share": '1/3 of plant dose', "products": 'NPK per plant + 40-50 t/ha FYM'},
        {"stage": '5th month', "share": '1/3 of plant dose', "products": 'NPK per plant'},
        {"stage": '7th month', "share": '1/3 of plant dose', "products": 'NPK per plant'},
    ],
    "barley": [
        {"stage": 'Basal (at sowing)', "share": 'Half N + full P & K', "products": 'DAP/MOP + 10 t/ha FYM'},
        {"stage": 'Tillering & flag leaf', "share": 'Remaining N', "products": 'Urea'},
    ],
    "bitter_gourd": [
        {"stage": 'Basal (at sowing)', "share": 'Half N + full P & K', "products": 'SSP/MOP + 20 t/ha FYM'},
        {"stage": '30 DAS', "share": 'Remaining N', "products": 'Urea'},
    ],
    "blackgram": [
        {"stage": 'Basal (at sowing)', "share": 'Full N, P & K', "products": 'SSP/MOP + 5 t/ha FYM; Rhizobium inoculation'},
    ],
    "blackpepper": [
        {"stage": 'May-June round', "share": 'Half season dose', "products": '10 kg FYM + 500 g neem cake + ash per vine'},
        {"stage": 'Sept-Oct round', "share": 'Half season dose', "products": 'NPK per vine'},
    ],
    "bottle_gourd": [
        {"stage": 'Basal (at sowing)', "share": 'Half N + full P & K', "products": 'SSP/MOP + 20-25 t/ha FYM'},
        {"stage": '30 DAS', "share": 'Remaining N', "products": 'Urea'},
    ],
    "brinjal": [
        {"stage": 'Basal (at transplanting)', "share": '50% N + full P & K', "products": 'DAP/MOP + 20-25 t/ha FYM'},
        {"stage": '30 & 60 DAT', "share": 'Remaining N in splits', "products": 'Urea'},
    ],
    "cabbage": [
        {"stage": 'Basal (at transplanting)', "share": '40% N + full P & K', "products": 'DAP/MOP + 20-25 t/ha FYM'},
        {"stage": '30 & 45 DAT', "share": 'Remaining N in 2 splits', "products": 'Urea'},
    ],
    "cardamom": [
        {"stage": 'May-June round', "share": 'Half season dose', "products": 'NPK + FYM + neem cake 2.9 t/ha'},
        {"stage": 'Sept-Oct round', "share": 'Half season dose', "products": 'NPK'},
    ],
    "cauliflower": [
        {"stage": 'Basal (at transplanting)', "share": '40% N + full P & K', "products": 'DAP/MOP + 25-30 t/ha FYM'},
        {"stage": '30 & 45 DAT', "share": 'Remaining N in 2 splits', "products": 'Urea'},
    ],
    "chickpea": [
        {"stage": 'Basal (at sowing)', "share": 'Full N, P & K', "products": 'SSP + 5 t/ha FYM; 2% urea foliar at flowering'},
    ],
    "coconut": [
        {"stage": 'First half-year split', "share": 'Half season dose', "products": 'NPK per palm + 50 kg FYM/year'},
        {"stage": 'Second half-year split', "share": 'Half season dose', "products": 'NPK per palm'},
    ],
    "coffee": [
        {"stage": 'June split', "share": 'Half season dose', "products": 'NPK per plant + FYM/vermicompost + Zn, B, Mo'},
        {"stage": 'September split', "share": 'Half season dose', "products": 'NPK per plant'},
    ],
    "coriander": [
        {"stage": 'Basal (at sowing)', "share": 'Half N + full P & K', "products": 'SSP/MOP + 10-15 t/ha FYM'},
        {"stage": '30 DAS', "share": 'Remaining N', "products": 'Urea'},
    ],
    "cotton": [
        {"stage": 'Basal (30% N + full P & K)', "share": '50 kg DAP + 25 kg MOP', "products": 'DAP + MOP'},
        {"stage": '30-35 DAS', "share": '30% N', "products": 'Urea'},
        {"stage": '60-65 DAS', "share": '40% N', "products": 'Urea'},
    ],
    "cucumber": [
        {"stage": 'Basal (at sowing)', "share": 'Half N + full P & K', "products": 'SSP/MOP + 20-25 t/ha FYM'},
        {"stage": '30 DAS', "share": 'Remaining N', "products": 'Urea'},
    ],
    "drumstick": [
        {"stage": 'First split', "share": 'Half season dose', "products": 'NPK + 10-15 kg FYM per bearing tree'},
        {"stage": 'Later splits', "share": 'Remaining N, P & K', "products": 'Urea/MOP'},
    ],
    "garlic": [
        {"stage": 'Basal (at planting)', "share": 'Full P & K + half N', "products": 'DAP/MOP + 20-25 t/ha FYM'},
        {"stage": '30 & 60 days', "share": 'Remaining N in 2 splits', "products": 'Urea'},
    ],
    "grapes": [
        {"stage": 'Splits by growth stage', "share": 'Divide season dose', "products": 'Fertigate 19:19:19 + urea alternately'},
    ],
    "horsegram": [
        {"stage": 'Basal (at sowing)', "share": 'Full N, P & K', "products": 'SSP + 7.5 t/ha FYM'},
    ],
    "jackfruit": [
        {"stage": 'Monsoon split', "share": 'Half season dose', "products": 'NPK + 50 kg FYM (bearing trees)'},
        {"stage": 'Post-monsoon split', "share": 'Half season dose', "products": 'NPK'},
    ],
    "jute": [
        {"stage": 'Basal (at sowing)', "share": '20 kg N + full P & K', "products": 'Urea/SSP + 5 t/ha FYM'},
        {"stage": '20-25 DAS', "share": '10 kg N', "products": 'Urea'},
        {"stage": '35-40 DAS', "share": '10 kg N', "products": 'Urea'},
    ],
    "kidneybeans": [
        {"stage": 'At planting', "share": 'Full N, P & K (balanced)', "products": 'Low-N compound + 5-10 t/ha FYM'},
    ],
    "lentil": [
        {"stage": 'Basal (at sowing)', "share": 'Full N, P & K', "products": 'SSP/MOP + 1-2 t/ha FYM; Sulphur 8 kg/acre'},
    ],
    "maize": [
        {"stage": 'Basal (at sowing)', "share": 'Half N + full P & K', "products": 'DAP/MOP + 12.5 t/ha FYM'},
        {"stage": 'Tasseling', "share": 'Remaining N', "products": 'Urea'},
    ],
    "mango": [
        {"stage": 'Monsoon split', "share": 'Half season dose', "products": 'NPK per tree + FYM (50 kg at maturity)'},
        {"stage": 'Post-monsoon split', "share": 'Half season dose', "products": 'NPK per tree'},
    ],
    "mothbeans": [
        {"stage": 'Basal (at sowing)', "share": 'Full N, P & K', "products": 'SSP/MOP + 4-5 t/ha FYM'},
    ],
    "mungbean": [
        {"stage": 'At sowing', "share": 'Full dose', "products": 'SSP 100 kg/acre + Zinc Sulphate 4-6 kg/acre'},
    ],
    "muskmelon": [
        {"stage": 'Basal (at sowing)', "share": 'Half N + full P & K', "products": 'SSP/MOP + 15-20 t/ha FYM'},
        {"stage": 'Vine growth', "share": 'Remaining N', "products": 'Urea'},
    ],
    "okra": [
        {"stage": 'Basal (at sowing)', "share": 'Half N + full P & K', "products": 'SSP/MOP + 15-20 t/ha FYM'},
        {"stage": 'Topdress splits', "share": 'Remaining N in 2 splits', "products": 'Urea'},
    ],
    "onion": [
        {"stage": 'Basal (at transplanting)', "share": 'Half N + full P & K', "products": 'DAP/MOP + 20-25 t/ha FYM'},
        {"stage": '30 & 45 DAT', "share": 'Remaining N in 2 splits', "products": 'Urea'},
    ],
    "orange": [
        {"stage": 'March (N split)', "share": 'Half N', "products": 'Urea per tree'},
        {"stage": 'October (N, P & K)', "share": 'Half N + full P & K', "products": 'NPK per tree + 30 kg FYM'},
    ],
    "papaya": [
        {"stage": 'Monthly splits', "share": '1/12 of annual dose monthly', "products": 'NPK per plant + 15-20 kg FYM/plant/year'},
    ],
    "pigeonpeas": [
        {"stage": 'Basal (at sowing)', "share": 'Full N, P & K', "products": 'SSP/MOP + 5-10 t/ha FYM; Zn 3 kg/ha, S 20 kg/ha if deficient'},
    ],
    "pineapple": [
        {"stage": 'Monthly splits (year-round)', "share": '1/12 of annual dose monthly', "products": 'NPK per plant + 5 kg FYM/plant/year; foliar micronutrients'},
    ],
    "pomegranate": [
        {"stage": 'Monsoon split', "share": 'Half season dose', "products": 'NPK per plant + calcium nitrate/SOP'},
        {"stage": 'Post-monsoon split', "share": 'Half season dose', "products": 'NPK per plant'},
    ],
    "potato": [
        {"stage": 'Basal (at planting)', "share": 'Full P & K + half N', "products": 'Sulphur-free K source/MOP + 20-25 t/ha FYM'},
        {"stage": 'Earthing up (30 DAS)', "share": 'Remaining N', "products": 'Urea'},
    ],
    "pumpkin": [
        {"stage": 'Basal (at sowing)', "share": 'Half N + full P & K', "products": 'SSP/MOP + 20-25 t/ha FYM'},
        {"stage": '30 DAS', "share": 'Remaining N', "products": 'Urea'},
    ],
    "radish": [
        {"stage": 'Basal (at sowing)', "share": 'Half N + full P & K', "products": 'SSP/MOP + 15-20 t/ha FYM'},
        {"stage": '25-30 DAS', "share": 'Remaining N', "products": 'Urea'},
    ],
    "ragi": [
        {"stage": 'Basal (at sowing)', "share": 'Half N + full P & K', "products": 'SSP/MOP + 7.5 t/ha FYM'},
        {"stage": '30 DAS', "share": 'Remaining N', "products": 'Urea'},
    ],
    "rapeseed": [
        {"stage": 'Basal (at sowing)', "share": 'Half N + full P, K & S', "products": 'DAP/MOP + 10 t/ha FYM'},
        {"stage": '30-35 DAS & flowering', "share": 'Remaining N', "products": 'Urea'},
    ],
    "rice": [
        {"stage": 'Basal (at transplanting)', "share": '50% N + full P & K', "products": 'DAP/MOP + 12.5 t/ha FYM'},
        {"stage": 'Tillering (20-25 DAT)', "share": '25% N', "products": 'Urea'},
        {"stage": 'Panicle initiation', "share": '25% N', "products": 'Urea'},
    ],
    "sorghum": [
        {"stage": 'Basal (at sowing)', "share": 'Half N + full P & K', "products": 'DAP/MOP + 10 t/ha FYM'},
        {"stage": '30-35 DAS', "share": 'Remaining N', "products": 'Urea'},
    ],
    "soybean": [
        {"stage": 'Basal (at sowing)', "share": 'Full N, P, K & S', "products": 'SSP/MOP + 5 t/ha FYM; Rhizobium inoculation'},
    ],
    "sunflower": [
        {"stage": 'Basal (at sowing)', "share": 'Half N + full P & K', "products": 'DAP/MOP + 12-15 t/ha FYM'},
        {"stage": '30 DAS', "share": 'Remaining N', "products": 'Urea; borax 0.2% foliar at flowering'},
    ],
    "sweet_potato": [
        {"stage": 'Basal (at planting)', "share": 'All P + half N & K', "products": 'SSP/MOP + 15-20 t/ha FYM'},
        {"stage": '30-40 DAS', "share": 'Remaining N & K', "products": 'Urea/MOP'},
    ],
    "tomato": [
        {"stage": 'Basal (at transplanting)', "share": '50% N + full P & K', "products": 'DAP/MOP + 25-30 t/ha FYM'},
        {"stage": 'Topdress splits', "share": 'Remaining N in 2 splits', "products": 'Urea; fertigation suits drip'},
    ],
    "turmeric": [
        {"stage": 'Basal (at planting)', "share": 'Part of N, P & K', "products": 'FYM 20 t + 2 t neem cake + 1 t ash + 4 t vermicompost'},
        {"stage": 'Splits (2-3 through season)', "share": 'Remaining N, P & K', "products": 'Urea/MOP'},
    ],
    "watermelon": [
        {"stage": 'Basal (at sowing)', "share": 'Full P & K', "products": 'SSP/MOP + 20 t/ha FYM'},
        {"stage": '30 days after sowing', "share": 'Full N', "products": 'Urea (or fertigate 200:100:100 NPK/ha)'},
    ],
    "wheat": [
        {"stage": 'Basal (at sowing)', "share": 'Full P & K + 1/3 N', "products": 'DAP/MOP + 10 t/ha FYM'},
        {"stage": 'CRI (root initiation)', "share": '1/3 N', "products": 'Urea'},
        {"stage": 'Tillering/jointing', "share": '1/3 N', "products": 'Urea'},
    ],
}

PEST_GUIDE = {
    "apple": [
        {"pest": 'scab', "treatment": 'Fungicides: Mancozeb, Captan for scab', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'codling moth', "treatment": 'Insecticides: Carbaryl for codling moth, Imidacloprid for aphids', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'aphids', "treatment": 'Insecticides: Carbaryl for codling moth, Imidacloprid for aphids', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "banana": [
        {"pest": 'sigatoka', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Fungicides: Bordeaux mixture, Copper oxychloride for Sigatoka'},
        {"pest": 'pseudostem weevil', "treatment": 'Insecticides: Monocrotophos for pseudostem weevil', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "barley": [
        {"pest": 'weed', "treatment": 'Herbicides: Isoproturon for weed control', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'rusts', "treatment": 'Fungicides: Propiconazole for rusts', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "bitter_gourd": [
        {"pest": 'fruit fly', "treatment": 'Insecticides: Imidacloprid for fruit fly', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'powdery mildew', "treatment": 'Fungicides: Carbendazim for powdery mildew', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "blackgram": [
        {"pest": 'pod borer', "treatment": 'Insecticides: Quinalphos for pod borer', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'wilt', "treatment": 'Fungicides: Carbendazim for wilt and leaf spot', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'leaf spot', "treatment": 'Fungicides: Carbendazim for wilt and leaf spot', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "blackpepper": [
        {"pest": 'foot rot', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Fungicides: Bordeaux mixture 1% for foot rot and diseases'},
    ],
    "bottle_gourd": [
        {"pest": 'aphids', "treatment": 'Insecticides: Imidacloprid for aphids', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'downy mildew', "treatment": 'Fungicides: Mancozeb for downy mildew', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "brinjal": [
        {"pest": 'fruit/shoot borer', "treatment": 'Insecticides: Spinosad for fruit/shoot borer', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'wilt', "treatment": 'Fungicides: Carbendazim for wilt, Mancozeb for phomopsis blight', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'phomopsis blight', "treatment": 'Fungicides: Carbendazim for wilt, Mancozeb for phomopsis blight', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "cabbage": [
        {"pest": 'diamond back moth', "treatment": 'for diamond back moth, Malathion for aphids', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'aphids', "treatment": 'for diamond back moth, Malathion for aphids', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'black rot', "treatment": 'Fungicides: Mancozeb for black rot', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "cardamom": [
        {"pest": 'thrips', "treatment": 'Insecticides: Quinalphos for thrips and shoot fly', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'shoot fly', "treatment": 'Insecticides: Quinalphos for thrips and shoot fly', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'leaf spot', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Fungicides: Bordeaux mixture for leaf spot'},
    ],
    "cauliflower": [
        {"pest": 'diamond back moth', "treatment": 'for diamond back moth, Carbaryl for caterpillars', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'caterpillars', "treatment": 'for diamond back moth, Carbaryl for caterpillars', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'black rot', "treatment": 'Fungicides: Mancozeb for black rot', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "chickpea": [
        {"pest": 'pod borer', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Insecticides: Endosulfan 0.07%, NPV 250 LE/ha for pod borer'},
        {"pest": 'ipm', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Spray 5% NSKE for IPM'},
    ],
    "coconut": [
        {"pest": 'rhinoceros beetle', "treatment": 'Insecticides: Monocrotophos for rhinoceros beetle', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'bud rot', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Fungicides: Bordeaux paste for bud rot'},
        {"pest": 'red palm weevil', "treatment": 'Root feeding of insecticides for red palm weevil', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "coffee": [
        {"pest": 'leaf rust', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Fungicides: Bordeaux mixture 1% for leaf rust'},
        {"pest": 'white stem borer', "treatment": 'Insecticides: Quinalphos for white stem borer', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "coriander": [
        {"pest": 'aphids', "treatment": 'Insecticides: Malathion for aphids', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'powdery mildew', "treatment": 'Fungicides: Mancozeb for powdery mildew and wilt', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'wilt', "treatment": 'Fungicides: Mancozeb for powdery mildew and wilt', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "cotton": [
        {"pest": 'bollworms', "treatment": 'Insecticides: Profenofos for bollworms, Acetamiprid for sucking pests', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'sucking pests', "treatment": 'Insecticides: Profenofos for bollworms, Acetamiprid for sucking pests', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'wilt', "treatment": 'Fungicides: Carbendazim for wilt', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "cucumber": [
        {"pest": 'aphids', "treatment": 'Insecticides: Imidacloprid for aphids', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'downy mildew', "treatment": 'Fungicides: Mancozeb for downy mildew, Carbendazim for anthracnose', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'anthracnose', "treatment": 'Fungicides: Mancozeb for downy mildew, Carbendazim for anthracnose', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "drumstick": [
        {"pest": 'pod fly', "treatment": 'Insecticides: Quinalphos for pod fly and caterpillars', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'caterpillars', "treatment": 'Insecticides: Quinalphos for pod fly and caterpillars', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'leaf spot diseases', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Fungicides: Bordeaux mixture for leaf spot diseases'},
    ],
    "garlic": [
        {"pest": 'purple blotch', "treatment": 'Fungicides: Mancozeb for purple blotch', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'thrips', "treatment": 'Insecticides: Dimethoate for thrips', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "grapes": [
        {"pest": 'downy/powdery mildew', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Fungicides: Bordeaux mixture, Mancozeb, Carbendazim for downy/powdery mildew'},
        {"pest": 'thrips', "treatment": 'Insecticides: Imidacloprid for thrips, Chlorpyriphos for mealy bugs', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'mealy bugs', "treatment": 'Insecticides: Imidacloprid for thrips, Chlorpyriphos for mealy bugs', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "horsegram": [
        {"pest": 'pod borer', "treatment": 'Insecticides: Chlorpyriphos for pod borer', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'eco-friendly pest', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Spray neem oil for eco-friendly pest control'},
    ],
    "jackfruit": [
        {"pest": 'soft rot', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Fungicides: Bordeaux paste for soft rot and dieback'},
        {"pest": 'dieback', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Fungicides: Bordeaux paste for soft rot and dieback'},
        {"pest": 'shoot', "treatment": 'Insecticides: Carbaryl for shoot and fruit borer', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'fruit borer', "treatment": 'Insecticides: Carbaryl for shoot and fruit borer', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "jute": [
        {"pest": 'hairy caterpillars', "treatment": 'Insecticides: Quinalphos for hairy caterpillars', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "kidneybeans": [
        {"pest": 'aphids', "treatment": 'Insecticides: Imidacloprid for aphids', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "lentil": [
        {"pest": 'aphids', "treatment": 'Insecticides for aphids and pod borer', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'pod borer', "treatment": 'Insecticides for aphids and pod borer', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "maize": [
        {"pest": 'shoot fly', "treatment": 'Insecticides: Carbofuran 33kg/ha for shoot fly, Chlorpyriphos for stem borer', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'stem borer', "treatment": 'Insecticides: Carbofuran 33kg/ha for shoot fly, Chlorpyriphos for stem borer', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "mango": [
        {"pest": 'fruit fly', "treatment": 'Insecticides: Malathion for fruit fly, Imidacloprid for hoppers', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'hoppers', "treatment": 'Insecticides: Malathion for fruit fly, Imidacloprid for hoppers', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'anthracnose', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Fungicides: Copper oxychloride for anthracnose, powdery mildew'},
        {"pest": 'powdery mildew', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Fungicides: Copper oxychloride for anthracnose, powdery mildew'},
    ],
    "mothbeans": [
        {"pest": 'pod borers', "treatment": 'Insecticides: Quinalphos or Monocrotophos for pod borers', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "mungbean": [
        {"pest": 'thrips', "treatment": 'Insecticides: Imidacloprid for thrips and aphids', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'aphids', "treatment": 'Insecticides: Imidacloprid for thrips and aphids', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "muskmelon": [
        {"pest": 'aphids', "treatment": 'Insecticides: Imidacloprid for aphids', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'downy mildew', "treatment": 'Fungicides: Mancozeb for downy mildew', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "okra": [
        {"pest": 'fruit borer', "treatment": 'Insecticides: Profenofos for fruit borer and jassids', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'jassids', "treatment": 'Insecticides: Profenofos for fruit borer and jassids', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'yellow vein mosaic (yvm) vector', "treatment": 'Fungicides: Carbendazim for yellow vein mosaic (YVM) vector control', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "onion": [
        {"pest": 'purple blotch', "treatment": 'Fungicides: Mancozeb for purple blotch', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'thrips', "treatment": 'Insecticides: Malathion for thrips', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'maggots', "treatment": 'Dimethoate for maggots', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "orange": [
        {"pest": 'citrus psylla', "treatment": 'Insecticides: Dimethoate for citrus psylla, Imidacloprid for leaf miner', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'leaf miner', "treatment": 'Insecticides: Dimethoate for citrus psylla, Imidacloprid for leaf miner', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'citrus canker', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Fungicides: Copper oxychloride for citrus canker'},
    ],
    "papaya": [
        {"pest": 'damping off', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Fungicides: Bordeaux mixture for damping off'},
        {"pest": 'fruit fly', "treatment": 'Insecticides: Malathion for fruit fly', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "pigeonpeas": [
        {"pest": 'pod borer', "treatment": 'Insecticides for pod borer', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "pineapple": [
        {"pest": 'heart rot', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Fungicides: Bordeaux mixture for heart rot'},
        {"pest": 'mealy bugs', "treatment": 'Insecticides: Malathion for mealy bugs', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'organic management', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Use neem oil for organic management'},
    ],
    "pomegranate": [
        {"pest": 'thrips', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Insecticides: Imidacloprid for thrips, Neem oil 0.5% for pests'},
    ],
    "potato": [
        {"pest": 'late blight', "treatment": 'Fungicides: Mancozeb for late blight, Metalaxyl for early blight', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'early blight', "treatment": 'Fungicides: Mancozeb for late blight, Metalaxyl for early blight', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'aphids', "treatment": 'Insecticides: Imidacloprid for aphids, Cartap for tuber moth', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'tuber moth', "treatment": 'Insecticides: Imidacloprid for aphids, Cartap for tuber moth', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "pumpkin": [
        {"pest": 'fruit fly', "treatment": 'Insecticides: Malathion for fruit fly', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'powdery mildew', "treatment": 'Fungicides: Mancozeb for powdery mildew', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "radish": [
        {"pest": 'aphids', "treatment": 'Insecticides: Malathion for aphids', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'leaf spot', "treatment": 'Fungicides: Mancozeb for leaf spot', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "ragi": [
        {"pest": 'shoot fly', "treatment": 'Insecticides: Chlorpyriphos for shoot fly', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'blast disease', "treatment": 'Fungicides: Carbendazim for blast disease', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "rapeseed": [
        {"pest": 'aphids', "treatment": 'Insecticides: Quinalphos for aphids, Chlorpyriphos for sawfly', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'sawfly', "treatment": 'Insecticides: Quinalphos for aphids, Chlorpyriphos for sawfly', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'alternaria blight', "treatment": 'Fungicides: Mancozeb for Alternaria blight', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "rice": [
        {"pest": 'stem borer', "treatment": 'Insecticides: Carbofuran 3CG 33kg/ha for stem borer', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'blast', "treatment": 'Fungicides: Carbendazim for blast', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "sorghum": [
        {"pest": 'shoot fly', "treatment": 'Insecticides: Chlorpyriphos for shoot fly, stem borer', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'stem borer', "treatment": 'Insecticides: Chlorpyriphos for shoot fly, stem borer', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'aphids', "treatment": 'Malathion for aphids', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "soybean": [
        {"pest": 'girdle beetle', "treatment": 'Insecticides: Quinalphos for girdle beetle and leaf eater', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'leaf eater', "treatment": 'Insecticides: Quinalphos for girdle beetle and leaf eater', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "sunflower": [
        {"pest": 'head borer', "treatment": 'Insecticides: Chlorpyriphos for head borer', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'rust', "treatment": 'Fungicides: Mancozeb for rust, Ridomil for downy mildew', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'downy mildew', "treatment": 'Fungicides: Mancozeb for rust, Ridomil for downy mildew', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "sweet_potato": [
        {"pest": 'weevil', "treatment": 'Insecticides: Chlorpyriphos for weevil', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'leaf spot', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Fungicides: Bordeaux mixture for leaf spot'},
    ],
    "tomato": [
        {"pest": 'fruit borer', "treatment": 'Insecticides: Profenofos for fruit borer', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'early blight', "treatment": 'Fungicides: Chlorothalonil for early blight, Mancozeb for late blight', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'late blight', "treatment": 'Fungicides: Chlorothalonil for early blight, Mancozeb for late blight', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "turmeric": [
        {"pest": 'shoot borer', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Spray Neem oil 0.5% for shoot borer'},
        {"pest": 'leaf spot', "treatment": 'Follow local label recommendations; scout and treat at early infestation', "organic": 'Bordeaux mixture 1% for leaf spot'},
    ],
    "watermelon": [
        {"pest": 'beetles', "treatment": 'Insecticides: Malathion for beetles', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
    "wheat": [
        {"pest": 'broadleaf weeds', "treatment": 'Herbicides: 2,4-D for broadleaf weeds, Isoproturon for grassy weeds', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'grassy weeds', "treatment": 'Herbicides: 2,4-D for broadleaf weeds, Isoproturon for grassy weeds', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
        {"pest": 'rusts', "treatment": 'Fungicides: Propiconazole for rusts', "organic": 'Neem oil 5 ml/L spray or Trichoderma seed/soil treatment as a general IPM measure'},
    ],
}

SOIL_FERT_PRACTICE = {
    "Alluvial": [
        'Naturally fertile — follow the standard schedule and top up with FYM each season',
        'Sandier river soils may still need split N; check texture with a ribbon test',
    ],
    "Black": [
        'High phosphorus fixation — apply the full P dose as basal together with FYM',
        'Watch potassium on heavy-feeding crops like cotton; gypsum can help structure',
    ],
    "Red": [
        'Often acidic — lime if pH is below 5.5 before planting',
        'Responsive to FYM and micronutrients (Zn, B); apply P with organic matter',
    ],
    "Sandy": [
        'Light texture leaches nutrients — split N into 3-4 small doses instead of one heavy application',
        'Fertigate frequently in small amounts; add FYM or compost to improve water/nutrient retention',
    ],
    "Loamy": [
        'Balanced structure — the standard split schedule works well',
        'Maintain 5-8% soil organic matter with regular FYM/compost for best nutrient holding',
    ],
    "Clayey": [
        'High nutrient retention — full basal doses are usually safe; still split N for efficiency',
        'Avoid waterlogging at the base; incorporate FYM at ploughing to improve drainage',
    ],
    "Laterite": [
        'Phosphorus fixation and low native K — add rock phosphate or extra organic matter',
        'Mulch heavily to conserve nutrients from heavy leaching rains',
    ],
}

SOURCE_NOTE = (
    "Fertilizer and pest guidance curated from the Comprehensive Crop Cultivation "
    "Dataset (Kaggle, Apache-2.0) and standard Indian agronomy references. Amounts "
    "are per-hectare season totals unless stated otherwise; always follow local "
    "extension advice and product labels."
)