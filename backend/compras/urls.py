from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import SolicitudCompraViewSet, SaldoCajaChicaView


router = DefaultRouter()

router.register(
    "solicitudes",
    SolicitudCompraViewSet,
    basename="solicitudes-compras"
)

urlpatterns = [
    path("caja-chica/saldo/", SaldoCajaChicaView.as_view(), name="compras-caja-chica-saldo"),
    path("saldo/", SaldoCajaChicaView.as_view(), name="compras-saldo"),
] + router.urls
