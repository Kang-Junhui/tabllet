from django.urls import path
from rest_framework.routers import DefaultRouter

from . import auth
from .views import MedicineViewSet, NutrientViewSet, PrescriptionViewSet

router = DefaultRouter()
router.register("prescriptions", PrescriptionViewSet, basename="prescription")
router.register("medicines", MedicineViewSet, basename="medicine")
router.register("nutrients", NutrientViewSet, basename="nutrient")

urlpatterns = [
    path("auth/register/", auth.register, name="auth-register"),
    path("auth/login/", auth.login, name="auth-login"),
    path("auth/logout/", auth.logout, name="auth-logout"),
    path("auth/me/", auth.me, name="auth-me"),
    *router.urls,
]
