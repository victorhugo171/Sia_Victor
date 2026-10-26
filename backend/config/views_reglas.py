"""
Vistas para la consulta centralizada de Reglas de Negocio del Sistema SIA.
Única Fuente de Verdad (Single Source of Truth) para Backend y Frontend.
"""
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class ReglasNegocioView(APIView):
    """
    Entrega todas las variables de negocio configuradas en settings.py.
    Permite que el Frontend se sincronice dinámicamente sin necesidad de
    valores estáticos ("quemados") en el código de Vue.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "limite_caja_chica": float(settings.SIA_LIMITE_CAJA_CHICA),
            "umbral_cotizaciones": float(settings.SIA_UMBRAL_COTIZACIONES),
            "min_cotizaciones": int(settings.SIA_MIN_COTIZACIONES),
            "categorias_prioridad_alta": list(settings.SIA_CATEGORIAS_PRIORIDAD_ALTA),
            "sla_horas": dict(settings.SIA_SLA_HORAS),
            "transiciones_estado": dict(settings.SIA_TRANSICIONES_ESTADO),
            "dias_reapertura": int(settings.SIA_DIAS_REAPERTURA),
            "max_tickets_tecnico": int(settings.SIA_MAX_TICKETS_ACTIVOS_TECNICO),
            "umbral_aprobacion_jefe": float(settings.SIA_UMBRAL_APROBACION_JEFE),
            "fondo_mensual": float(settings.SIA_FONDO_MENSUAL),
            "min_password_length": int(settings.SIA_MIN_PASSWORD_LENGTH),
        })
