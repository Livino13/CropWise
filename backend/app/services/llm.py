"""Shared Gemini client (OpenAI-compatible endpoint) with model fallback."""
import logging
from typing import Optional

import httpx

from ..core.config import settings

logger = logging.getLogger(__name__)


class LLMUnavailable(Exception):
    """Friendly, user-safe failure from the model provider."""


async def generate_chat(
    messages: list[dict],
    *,
    max_tokens: int = 2048,
    temperature: float = 0.4,
    timeout: float = 30.0,
) -> str:
    if not settings.LLM_API_KEY:
        raise LLMUnavailable("The AI assistant is not configured yet.")

    url = f"{settings.LLM_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    models = list(
        dict.fromkeys(
            model
            for model in (settings.LLM_MODEL, settings.LLM_FALLBACK_MODEL)
            if model
        )
    )

    data: Optional[dict] = None
    last_status: Optional[int] = None
    async with httpx.AsyncClient(timeout=timeout) as client:
        for model in models:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            try:
                resp = await client.post(url, headers=headers, json=payload)
            except httpx.HTTPError:
                logger.warning("LLM request failed for %s", model)
                continue

            if resp.status_code < 400:
                try:
                    data = resp.json()
                except ValueError:
                    logger.warning("LLM returned invalid JSON for %s", model)
                    last_status = 502
                    continue
                break

            last_status = resp.status_code
            logger.warning(
                "LLM request failed with %s (%s): %s",
                model,
                resp.status_code,
                resp.text[:300],
            )
            if resp.status_code in (400, 401, 403):
                break

    if data is None:
        if last_status == 429:
            raise LLMUnavailable(
                "The assistant is getting a lot of questions right now. "
                "Please try again in a minute."
            )
        if last_status and last_status >= 500:
            raise LLMUnavailable(
                "The assistant is busy right now. Please try again in a moment."
            )
        raise LLMUnavailable(
            "The assistant is temporarily unavailable. Please try again later."
        )

    try:
        reply = str(data["choices"][0]["message"]["content"]).strip()
    except (KeyError, IndexError, TypeError, AttributeError):
        raise LLMUnavailable(
            "The assistant returned an unexpected response. Please try again."
        )
    if not reply:
        raise LLMUnavailable(
            "The assistant returned an empty response. Please try again."
        )
    return reply
