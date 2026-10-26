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
            "limite_caja_chica": float(getattr(settings, "SIA_LIMITE_CAJA_CHICA", 1000.0)),
            "umbral_cotizaciones": float(getattr(settings, "SIA_UMBRAL_COTIZACIONES", 500.0)),
            "min_cotizaciones": int(getattr(settings, "SIA_MIN_COTIZACIONES", 3)),
            "categorias_prioridad_alta": list(getattr(settings, "SIA_CATEGORIAS_PRIORIDAD_ALTA", ["RED", "SERVIDORES"])),
            "sla_horas": dict(getattr(settings, "SIA_SLA_HORAS", {"ALTA": 4, "MEDIA": 24, "BAJA": 72})),
            "transiciones_estado": dict(getattr(settings, "SIA_TRANSICIONES_ESTADO", {
                "ABIERTO": ["EN_PROCESO"],
                "EN_PROCESO": ["RESUELTO"],
                "RESUELTO": ["CERRADO", "EN_PROCESO"],
                "CERRADO": ["EN_PROCESO"],
            })),
            "dias_reapertura": int(getattr(settings, "SIA_DIAS_REAPERTURA_TICKET", 7)),
            "max_tickets_tecnico": int(getattr(settings, "SIA_MAX_TICKETS_ACTIVOS_TECNICO", 5)),
            "umbral_aprobacion_jefe": float(getattr(settings, "SIA_UMBRAL_APROBACION_JEFE", 300.0)),
            "fondo_mensual": float(getattr(settings, "SIA_FONDO_MENSUAL", 5000.0)),
            "min_password_length": int(getattr(settings, "SIA_MIN_PASSWORD_LENGTH", 10)),
        })
