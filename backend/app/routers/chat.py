"""CropWise chat assistant.

Proxies a Gemini model through its OpenAI-compatible endpoint so the API key
never reaches the browser. Answers are grounded with app crop facts (sent by
the client) and agronomy guidance from services.agronomy.
"""
import logging
import re

from fastapi import APIRouter, HTTPException

from ..core.config import settings
from ..schemas.chat import ChatRequest, ChatResponse
from ..services.agronomy import (
    CROP_NPK_TARGET,
    DOSE_UNIT,
    FERTILIZER_STAGES,
    PEST_GUIDE,
)
from ..services.llm import LLMUnavailable, generate_chat

router = APIRouter(prefix="/api", tags=["chat"])
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are CropWise Assistant, a friendly farm advisor built into the CropWise crop-recommendation app.

Who you talk to: small and marginal farmers. Use simple English, short paragraphs (2-4 sentences), and avoid ML or technical jargon.

What you help with:
- Crop choices, seasons (Kharif/Rabi/Zaid/perennial) and water needs
- Soil nutrients (N, P, K), soil pH, rainfall and humidity
- Pests and fertilizer basics for supported crops
- How to use the CropWise app

Rules:
- Use only the crop facts and guidance provided below plus general, safe agronomy knowledge. Never invent numbers.
- For pesticide or fertilizer quantities, share only the guidance below and tell the farmer to follow the product label or ask a local agronomist.
- If a question depends on soil values, suggest a soil test.
- If asked something unrelated to farming or CropWise, politely steer back.
- Keep answers practical and encouraging. Use short bullet points when listing crops or steps.
- Confidence levels in the app: Excellent match (70%+), Good match (40-69%), Moderate (below 40%). The top 3 are best matches, not guarantees.

App guide:
- New Recommendation: enter N, P, K and pH plus temperature, humidity and rainfall (or auto-fill weather) to get the top 3 crops.
- Fields: save fields and soil test values.
- History: past recommendations; record the crop actually planted to improve future accuracy.
- Crop Guide: crop details by season, water need, description, pests and nutrient needs.
"""

SOIL_TERMS = """Soil terms:
- N (nitrogen): supports leaf and stem growth; low N often means pale, yellowish leaves.
- P (phosphorus): supports roots, flowering and early growth.
- K (potassium): supports overall plant health, disease resistance and grain or fruit quality.
- pH: how acidic or alkaline the soil is; most crops do best between about 6 and 7.5.
- Rainfall: water available across the season.
- Humidity: moisture in the air; high humidity can raise disease pressure.
"""


def _mentioned_crops(text: str) -> list[str]:
    lowered = text.lower()
    found: list[str] = []
    for crop in PEST_GUIDE:
        spaced = crop.replace("_", " ")
        variants = {crop, spaced, spaced.replace(" ", "")}
        pattern = "|".join(rf"\b{re.escape(v)}s?\b" for v in variants)
        if re.search(pattern, lowered):
            found.append(crop)
    return found[:3]


def _crop_guidance(text: str) -> str:
    blocks: list[str] = []
    for crop in _mentioned_crops(text):
        lines = [f"Guidance for {crop.replace('_', ' ')}:"]
        target = CROP_NPK_TARGET.get(crop)
        unit = DOSE_UNIT.get(crop, "kg/ha")
        if target:
            lines.append(
                f"- Season nutrient target: N {target['n']:g}, P {target['p']:g}, "
                f"K {target['k']:g} ({unit})."
            )
        stages = FERTILIZER_STAGES.get(crop, [])
        if stages:
            parts = "; ".join(
                f"{s['stage']} — {s['share']}: {s['products']}" for s in stages[:3]
            )
            lines.append(f"- Fertilizer stages: {parts}.")
        pests = PEST_GUIDE.get(crop, [])
        if pests:
            parts = "; ".join(
                f"{p['pest']} (chemical: {p['treatment']}; organic: {p['organic']})"
                for p in pests[:3]
            )
            lines.append(f"- Common pests: {parts}.")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not settings.LLM_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Chat assistant is not configured. Add LLM_API_KEY to backend/.env.",
        )

    last_user = next(
        (m.content for m in reversed(req.messages) if m.role == "user"), ""
    )

    parts = [SYSTEM_PROMPT, SOIL_TERMS]
    if req.context:
        parts.append(f"Crop facts supplied by the app:\n{req.context.strip()}")
    guidance = _crop_guidance(last_user)
    if guidance:
        parts.append(guidance)
    system_prompt = "\n\n".join(parts)

    payload_messages = [
        {"role": "system", "content": system_prompt},
        *({"role": m.role, "content": m.content} for m in req.messages[-10:]),
    ]
    try:
        reply = await generate_chat(payload_messages, max_tokens=2048)
    except LLMUnavailable as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return ChatResponse(reply=reply)
