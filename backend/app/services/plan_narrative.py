"""Turn an already-computed crop plan into a farmer-friendly explanation.

The model is never asked to calculate or change a number — it only explains the
plan produced by services.crop_plan. Successful explanations are cached by plan
content so repeated card views do not spend free-tier quota.
"""
import hashlib
import json

from .llm import LLMUnavailable, generate_chat

_CACHE: dict[str, str] = {}
_MAX_CACHE = 300

SYSTEM_PROMPT = """You are CropWise Assistant, a friendly farm advisor for small and marginal farmers.

You will receive a crop plan that has ALREADY been calculated. Explain it in simple English in 120-180 words.

Strict rules:
- Never change, recalculate, round differently, or invent any number, fertilizer product or dose.
- Use only the values in the plan. If a value is missing, say that a soil test is needed.
- Explain the sowing window, the water advice, the fertilizer products and stages, and the main risk in that order.
- Mention that product grades should be confirmed with the local dealer or agriculture officer.
- Keep it practical, short and encouraging. Use short bullet points where helpful.
"""


async def explain_plan(plan: dict) -> str | None:
    payload = {
        "crop": plan.get("crop"),
        "field": plan.get("field"),
        "growing": plan.get("growing"),
        "fertilizer": plan.get("fertilizer"),
        "basis": plan.get("basis"),
    }
    key = hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode()
    ).hexdigest()
    cached = _CACHE.get(key)
    if cached:
        return cached

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": "Calculated plan (do not change any number):\n"
            + json.dumps(payload, ensure_ascii=False, default=str),
        },
    ]
    try:
        text = await generate_chat(messages, max_tokens=2048, temperature=0.3)
    except LLMUnavailable:
        return None

    _CACHE[key] = text
    if len(_CACHE) > _MAX_CACHE:
        _CACHE.pop(next(iter(_CACHE)))
    return text
