"""LLM refinement server client: raw HIRA records -> per-drug nutrient picks.

Expected contract (LLM server):
    POST {LLM_SERVER_URL}/extract   (application/json)
        {"메피론정": [<HIRA record>, ...],          # same shape as the HIRA cache
         "아레온정": [<HIRA record>, ...]}
    -> 200 {
         "메피론정": {"positive": ["염분", "칼륨"], "caution": ["나트륨"]},
         "아레온정": {"positive": [],               "caution": ["알코올"]}
       }

The call is batched: send every drug at once, keyed by name; the response is
keyed by the same names. The server already classifies nutrients with the
IngredientNutrient effect vocabulary — `positive` (보충 권장) and `caution`
(제한 권장) — so ingest stores them directly. Drug ingredients and excipients
(e.g. 유당) are filtered out server-side.
"""
import httpx
from django.conf import settings

from .base import ExternalServiceError, client


def refine_drugs(drugs: dict[str, list[dict]]) -> dict[str, dict]:
    """Batch-refine raw HIRA records into {name: {supplement, avoid}}."""
    if not settings.LLM_SERVER_URL:
        raise ExternalServiceError("LLM_SERVER_URL is not configured")
    if not drugs:
        return {}

    url = settings.LLM_SERVER_URL.rstrip("/") + "/extract"
    try:
        with client() as c:
            res = c.post(url, json=drugs)
            res.raise_for_status()
            data = res.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise ExternalServiceError(f"LLM refine failed: {exc}") from exc

    if not isinstance(data, dict):
        raise ExternalServiceError("LLM refine returned a non-object payload")
    return data
