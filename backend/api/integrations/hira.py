"""HIRA/MFDS DrugPrdtPrmsnInfoService client.

Ported from reference/hira_extract.py. Looks a drug up by name and returns its
사용상의주의사항 (NB_DOC_DATA) as cleaned text blocks — the only field the LLM
refinement step needs. Responses are cached on disk (HIRA_CACHE_PATH), seeded
from reference/hira_res.json, so repeated/known drugs need no network call.
"""
import html
import json
import re
import urllib.parse
from pathlib import Path

import httpx
from django.conf import settings

from .base import ExternalServiceError, client


def _encoded_key() -> str:
    """Normalize the service key to a singly URL-encoded form (as the API wants)."""
    raw = settings.HIRA_API_KEY
    return urllib.parse.quote(urllib.parse.unquote(raw), safe="")


def _extract_cdata(raw: str | None) -> list[str]:
    """Pull CDATA blocks out of a *_DOC_DATA field and strip their markup."""
    out = []
    for c in re.findall(r"<!\[CDATA\[(.*?)\]\]>", raw or "", re.S):
        c = html.unescape(c).replace("&nbsp;", " ")
        c = re.sub(r"<[^>]+>", " ", c)
        c = re.sub(r"\s+", " ", c).strip()
        if c:
            out.append(c)
    return out


def _load_cache() -> dict:
    path = Path(settings.HIRA_CACHE_PATH)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _save_cache(cache: dict) -> None:
    path = Path(settings.HIRA_CACHE_PATH)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        # Caching is best-effort; a read-only FS shouldn't break ingest.
        pass


def _fetch_live(name: str) -> list[dict]:
    if not settings.HIRA_API_KEY:
        raise ExternalServiceError("HIRA_API_KEY is not configured")
    params = {"pageNo": "1", "numOfRows": "20", "item_name": name, "type": "json"}
    url = f"{settings.HIRA_BASE_URL}?serviceKey={_encoded_key()}&{urllib.parse.urlencode(params)}"
    try:
        with client() as c:
            res = c.get(url)
            res.raise_for_status()
            data = res.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise ExternalServiceError(f"HIRA request failed for {name!r}: {exc}") from exc
    items = data.get("body", {}).get("items", [])
    return [items] if isinstance(items, dict) else (items or [])


def fetch_records(name: str) -> list[dict]:
    """Return the raw HIRA records for a drug (cache-first, then live API).

    These raw records are what the LLM refinement server consumes (it does its
    own NB_DOC_DATA parsing). Returns an empty list if the drug isn't in HIRA.
    """
    cache = _load_cache()
    items = cache.get(name)
    if items is None:
        items = _fetch_live(name)
        cache[name] = items
        _save_cache(cache)
    return items or []


def summarize(name: str, items: list[dict]) -> dict | None:
    """Distill raw HIRA records into {item_name, ingredient, 사용상의주의사항}.

    Pure: operates on already-fetched records so callers can reuse them for the
    refine payload without a second cache read. None if there are no records.
    """
    if not items:
        return None
    it = items[0]
    return {
        "item_name": it.get("ITEM_NAME") or name,
        "ingredient": it.get("MAIN_ITEM_INGR") or it.get("INGR_NAME") or "",
        "사용상의주의사항": _extract_cdata(it.get("NB_DOC_DATA")),
    }


def fetch_precautions(name: str) -> dict | None:
    """Convenience: fetch records and summarize in one call (cache-first)."""
    return summarize(name, fetch_records(name))
