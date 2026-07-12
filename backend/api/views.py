"""API views. Skinny by design: business logic lives in services.py / ingest.py."""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from . import ingest
from .integrations.base import ExternalServiceError
from .models import Medicine, Nutrient, Prescription
from .serializers import (
    MedicineSerializer,
    NutrientSerializer,
    PrescriptionSerializer,
    RecommendationResultSerializer,
)
from .services import recommend_for_prescription


class NutrientViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/nutrients/ — reference list of nutrients."""

    queryset = Nutrient.objects.all()
    serializer_class = NutrientSerializer


class MedicineViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/medicines/ — drug catalog with ingredients."""

    queryset = Medicine.objects.prefetch_related("ingredients").all()
    serializer_class = MedicineSerializer


class PrescriptionViewSet(viewsets.ModelViewSet):
    """CRUD for prescriptions plus the nutrient recommendation action.

        POST /api/prescriptions/                 register a prescription
        GET  /api/prescriptions/{id}/            prescription detail
        GET  /api/prescriptions/{id}/recommendations/   needed / caution nutrients
    """

    serializer_class = PrescriptionSerializer

    def get_queryset(self):
        # IsAuthenticated is enforced globally, so request.user is a real user;
        # a prescription is only ever visible to its owner.
        return Prescription.objects.filter(
            user=self.request.user
        ).prefetch_related("items__medicine")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get"])
    def recommendations(self, request, pk=None):
        result = recommend_for_prescription(self.get_object())
        return Response(RecommendationResultSerializer(result).data)

    @action(
        detail=False,
        methods=["post"],
        parser_classes=[MultiPartParser, FormParser],
    )
    def scan(self, request):
        """POST /api/prescriptions/scan/ — multipart `image`.

        Runs OCR -> HIRA -> LLM ingest and reports each recognized drug's status
        (existing / imported / not_found). Catalogued medicines can then be used
        to build a prescription.
        """
        image = request.FILES.get("image")
        if image is None:
            return Response(
                {"detail": "multipart field 'image' is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            result = ingest.scan_prescription_image(
                image.read(), image.name, image.content_type
            )
        except ExternalServiceError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY
            )
        return Response(result)

    @action(detail=False, methods=["post"])
    def resolve(self, request):
        """POST /api/prescriptions/resolve/ — JSON {"names": [...]}.

        Re-runs HIRA -> LLM ingest for a manually corrected/added name list
        (no OCR). Lets the user fix misrecognized names before building a
        prescription. Returns the same shape as scan.
        """
        names = request.data.get("names")
        if not isinstance(names, list):
            return Response(
                {"detail": "'names' must be a list of drug names"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cleaned = [str(n) for n in names if str(n).strip()]
        if not cleaned:
            return Response(
                {"detail": "at least one drug name is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            result = ingest.resolve_drug_names(cleaned)
        except ExternalServiceError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY
            )
        return Response(result)
