"""Unified API response envelope: {"success", "data", "error"}.

Applied globally via DRF settings so the frontend gets one consistent shape for
every endpoint (CLAUDE.md "응답 규격 통일"). Success responses wrap the payload
in `data`; error responses (status >= 400) move the payload into `error`.
"""
from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler as drf_exception_handler


class EnvelopeJSONRenderer(JSONRenderer):
    """Wrap every JSON response in the unified envelope."""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        response = renderer_context.get("response")
        status_code = getattr(response, "status_code", 200)

        # Already enveloped (e.g. re-rendered) — don't double-wrap.
        if isinstance(data, dict) and data.keys() >= {"success", "data", "error"}:
            envelope = data
        elif status_code >= 400:
            envelope = {"success": False, "data": None, "error": data}
        else:
            envelope = {"success": True, "data": data, "error": None}

        return super().render(envelope, accepted_media_type, renderer_context)


def envelope_exception_handler(exc, context):
    """Ensure unhandled/`raise`d DRF exceptions still produce the envelope.

    The renderer handles the wrapping; this just guarantees DRF returns a
    Response (so the renderer runs) for the exceptions it knows about.
    """
    return drf_exception_handler(exc, context)
