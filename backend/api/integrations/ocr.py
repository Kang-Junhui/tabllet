"""OCR server client: prescription image -> recognized drug names.

Expected contract (OCR server):
    POST {OCR_SERVER_URL}/extract   (multipart/form-data, field "image")
    -> 200 {"drugs": ["메피론정", "아레온정", ...]}

The server strips dosage/unit suffixes (e.g. "메피론정4mg" -> "메피론정") so the
names line up with the HIRA catalog keys.

Also tolerated: {"drug_names": [...]} or a list of {"name": "..."} objects.
"""
import httpx
from django.conf import settings

from .base import ExternalServiceError, client


def _parse_names(payload) -> list[str]:
    if isinstance(payload, dict):
        payload = payload.get("drugs") or payload.get("drug_names") or []
    names = []
    for entry in payload or []:
        name = entry.get("name") if isinstance(entry, dict) else entry
        if isinstance(name, str) and name.strip():
            names.append(name.strip())
    # De-duplicate while preserving order.
    return list(dict.fromkeys(names))


def extract_drug_names(image_bytes: bytes, filename: str, content_type: str) -> list[str]:
    if not settings.OCR_SERVER_URL:
        raise ExternalServiceError("OCR_SERVER_URL is not configured")

    url = settings.OCR_SERVER_URL.rstrip("/") + "/extract"
    files = {"image": (filename or "image", image_bytes, content_type or "application/octet-stream")}
    try:
        with client() as c:
            res = c.post(url, files=files)
            res.raise_for_status()
            return _parse_names(res.json())
    except (httpx.HTTPError, ValueError) as exc:
        raise ExternalServiceError(f"OCR request failed: {exc}") from exc
