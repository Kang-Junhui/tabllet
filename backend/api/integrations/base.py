"""Shared helpers for external-service clients."""
import httpx
from django.conf import settings


class ExternalServiceError(Exception):
    """Raised when an OCR/LLM/HIRA call fails or is misconfigured.

    The API layer maps this to a 502/503 response inside the standard envelope.
    """


def client() -> httpx.Client:
    """An httpx client with the project-wide timeout applied."""
    return httpx.Client(timeout=settings.EXTERNAL_HTTP_TIMEOUT)
