from decimal import Decimal
from urllib.parse import urlsplit
from django.conf import settings
from rest_framework import serializers
import re

from usuarios.archivos import firmar_urls
from .models import SolicitudCompra


class MontoEstimadoField(serializers.DecimalField):
    def to_internal_value(self, data):
        if not re.fullmatch(r"[0-9]+(?:\.[0-9]{1,2})?", str(data)):
            raise serializers.ValidationError("Ingrese un monto numérico con hasta dos decimales.")
        return super().to_internal_value(data)


# ==========================================================
# ARCHIVOS DEL EXPEDIENTE
# ==========================================================
#
# Se sirven como ruta relativa ("/media/...") en vez de URL
# absoluta con el host interno del backend (127.0.0.1:8000),
# que nunca es alcanzable desde fuera de esta máquina. El
# frontend (Vite) reenvía /media al backend, así que la ruta
# relativa siempre resuelve contra el mismo origen que sirvió
# la página (localhost o el túnel público).
# ==========================================================

CAMPOS_ARCHIVO = (
    "informe", "poa", "pedido", "proforma",
    "certificacion_presupuestaria",
    "factura", "acta_conformidad", "fotograma",
)


class SolicitudCompraSerializer(serializers.ModelSerializer):
    receptor_acta = serializers.SerializerMethodField()

    def get_receptor_acta(self, obj):
        from .actas_almacen import receptor_acta
        receptor = receptor_acta(obj)
        return {
            'id': receptor.pk,
            'nombre': receptor.nombre_completo,
            'tecnico': bool(obj.requerimiento_mantenimiento_id or obj.ticket_soporte_id)
        } if receptor else None

    monto_estimado = MontoEstimadoField(max_digits=12, decimal_places=2, min_value=0, required=False, allow_null=True)
    cotizaciones = serializers.ListField(required=False, write_only=True)

    # --- REGLA 01: Validación de Límite de Caja Chica ---
    def validate_monto_estimado(self, value):
        # Lee la variable SIA_LIMITE_CAJA_CHICA dinámicamente desde settings (por defecto 1000.0)
        limite_val = getattr(settings, 'SIA_LIMITE_CAJA_CHICA', 1000.0)
        limite = Decimal(str(limite_val))
        if value is not None and value > limite:
            raise serializers.ValidationError(
                f"El monto del requerimiento (Bs {value:.2f}) supera el límite máximo permitido de Caja Chica (Bs {limite:.2f})."
            )
        return value

    # El expediente dice por sí mismo de quién depende ahora: evita que
    # cada área tenga que preguntar en qué punto va el trámite.
    responsable_actual = serializers.SerializerMethodField()
    situacion = serializers.SerializerMethodField()

    solicitante_nombre = serializers.CharField(
        source="solicitante.nombre_completo",
        read_only=True
    )

    solicitante_email = serializers.CharField(
        source="solicitante.email",
        read_only=True
    )

    area_nombre = serializers.CharField(
        source="area.nombre",
        read_only=True
    )

    estado_nombre = serializers.CharField(
        source="get_estado_display",
        read_only=True
    )

    tipo_nombre = serializers.CharField(
        source="get_tipo_display",
        read_only=True
    )

    via_nombre = serializers.CharField(
        source="get_via_adquisicion_display",
        read_only=True
    )

    class Meta:
        model = SolicitudCompra
        fields = [
            "id",
            "codigo",
            "titulo",
            "descripcion",
            "solicitante",
            "solicitante_nombre", "receptor_acta",
            "solicitante_email",
            "area",
            "area_nombre",
            "tipo",
            "tipo_nombre",
            "cantidad",
            "especificaciones",
            "justificacion",
            "centro_costo",
            "monto_estimado",
            "cotizaciones",
            "via_adquisicion",
            "via_nombre",
            "estado",
            "estado_nombre",
            "responsable_actual",
            "situacion",
            "origen_modulo",
            "ticket_soporte",
            "requerimiento_mantenimiento",
            "ticket_soporte_vinculado",
            "observaciones",
            "informe", "poa", "pedido", "proforma",
            "certificacion_presupuestaria",
            "factura", "acta_conformidad", "fotograma",
            "motivo_rechazo", "monto_desembolsado",
            "tipo_desembolso", "comprobante_desembolso",
            "fondos_recibidos_en", "fondos_recibidos_por",
            "gestion_estado", "gestion_nota", "gestion_actualizada_en",
            "responsable_adquisicion", "monto_real", "proveedor",
            "componente_verificado", "observacion_verificacion",
            "comprobante_compra", "fecha_compra",
            "cantidad_recibida", "responsable_recepcion", "observacion_ingreso",
            "cantidad_entregada", "entregado_a", "observacion_salida",
            "fecha_ingreso_almacen", "fecha_despacho_almacen",
            "fecha_entrega_solicitante", "acta_firmada_en", "solicitud_recibida_en",
            "cerrado_inmutable",
            "activo",
            "creado_en",
            "actualizado_en",
        ]

        read_only_fields = [
            "codigo",
            "solicitante",
            "estado",
            "via_adquisicion",
            "origen_modulo",
            "ticket_soporte",
            "requerimiento_mantenimiento",
            "ticket_soporte_vinculado",
            "observaciones",
            "certificacion_presupuestaria", "factura",
            "acta_conformidad", "fotograma", "motivo_rechazo",
            "monto_desembolsado", "responsable_adquisicion",
            "monto_real", "proveedor",
            "componente_verificado", "observacion_verificacion",
            "comprobante_compra", "fecha_compra",
            "cantidad_recibida", "responsable_recepcion", "observacion_ingreso",
            "cantidad_entregada", "entregado_a", "observacion_salida",
            "fecha_ingreso_almacen", "fecha_despacho_almacen",
            "fecha_entrega_solicitante", "acta_firmada_en", "solicitud_recibida_en",
            "cerrado_inmutable",
            "creado_en",
            "actualizado_en",
        ]

    ETAPAS = {
        "CREADO_PENDIENTE_DAF": ("DAF", "Verificar los requisitos del expediente"),
        "EVALUADO_PENDIENTE_CERTIFICACION": ("DAF", "Emitir la certificación presupuestaria"),
        "VERIFICADO_PENDIENTE_AUTORIZACION": ("Director", "Autorizar la compra"),
        "APROBADO_PARA_DESEMBOLSO": ("Tesorería", "Desembolsar el dinero"),
        "COMPRA_REGISTRADA": ("Compras y Almacén", "Registrar los movimientos de almacén"),
        "COMPRADO_Y_ENTREGADO": ("Sección solicitante", "Firmar el acta de conformidad"),
        "DESCARGO_PENDIENTE_LIQUIDACION": ("Sección solicitante", "Recibir formalmente la solicitud"),
        "CERRADO_ARCHIVADO": ("", "Proceso concluido"),
        "RECHAZADO": ("", "Expediente rechazado"),
        "ANULADO": ("", "Expediente anulado"),
    }

    def get_responsable_actual(self, obj):
        if obj.estado == "FONDOS_DESEMBOLSADOS":
            return "Compras y Almacén"
        return self.ETAPAS.get(obj.estado, ("", ""))[0]

    def get_situacion(self, obj):
        """Frase corta que explica en qué punto está el trámite."""
        if obj.estado == "FONDOS_DESEMBOLSADOS":
            if not obj.fondos_recibidos_en:
                return "Fondos listos para retirar en Tesorería"
            if obj.gestion_estado:
                texto = dict(SolicitudCompra.GESTIONES)[obj.gestion_estado]
                return f"{texto}{f' — {obj.gestion_nota}' if obj.gestion_nota else ''}"
            return "Efectivo recibido — pendiente de realizar la compra"

        if obj.estado == "COMPRA_REGISTRADA":
            if not obj.fecha_ingreso_almacen:
                return "Comprado — pendiente de registrar la entrada a almacén"
            if not obj.fecha_despacho_almacen:
                return "En almacén — pendiente de registrar la salida"
            return "Salida registrada — pendiente de entregar con acta"

        return self.ETAPAS.get(obj.estado, ("", obj.get_estado_display()))[1]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Metadato solicitado únicamente por la bandeja de Tesorería.
        if hasattr(instance, 'tesoreria_fecha'):
            data['tesoreria_fecha'] = instance.tesoreria_fecha.isoformat() if instance.tesoreria_fecha else None

        for campo in CAMPOS_ARCHIVO:
            valor = data.get(campo)
            if valor:
                data[campo] = urlsplit(valor).path

        return firmar_urls(data, self.context.get('request'))

    def create(self, validated_data):
        validated_data.pop('cotizaciones', None)
        request = self.context["request"]
        usuario = request.user
        return SolicitudCompra.objects.create(
            codigo=SolicitudCompra.generar_codigo(),
            solicitante=usuario,
            estado="CREADO_PENDIENTE_DAF",
            **validated_data
        )

    def validate(self, attrs):
        # === REGLA 02: Tres cotizaciones de proveedores distintos para compras > Bs 500 ===
        monto = attrs.get('monto_estimado')
        if monto is None and self.instance:
            monto = self.instance.monto_estimado
        if monto and float(monto) > 500:
            cotizaciones = attrs.get('cotizaciones')
            if cotizaciones is None:
                cotizaciones = self.initial_data.get('cotizaciones')
            if cotizaciones is None and self.instance:
                cotizaciones = list(self.instance.cotizaciones.all())
            cotizaciones = cotizaciones or []

            # 1. Validar cantidad mínima de 3 cotizaciones
            if len(cotizaciones) < 3:
                raise serializers.ValidationError({
                    "cotizaciones": "Toda compra mayor a Bs 500.00 requiere adjuntar al menos 3 cotizaciones."
                })

            # 2. Validar que los proveedores sean distintos
            proveedores = set()
            for cot in cotizaciones:
                prov = cot.get('proveedor') if isinstance(cot, dict) else getattr(cot, 'proveedor', None)
                if prov:
                    proveedores.add(str(prov).strip().lower())

            if len(proveedores) < 3:
                raise serializers.ValidationError({
                    "cotizaciones": "Las 3 cotizaciones deben pertenecer a proveedores distintos."
                })

        # BPMN: la solicitud viaja respaldada por Informe, Proforma y POA.
        # El "pedido" se conserva como documento opcional del expediente.
        if self.instance is None:
            faltantes = [
                nombre for nombre in ("informe", "proforma", "poa")
                if not attrs.get(nombre)
            ]
            if faltantes:
                raise serializers.ValidationError({
                    "documentos": "Debe adjuntar Informe, Proforma y POA. Faltan: " + ", ".join(faltantes)
                })

        # Se exige PDF para que el expediente sea previsualizable
        # (el navegador no puede renderizar .docx/.pptx en línea).
        no_pdf = [
            nombre for nombre in ("informe", "poa", "pedido")
            if attrs.get(nombre) and not attrs[nombre].name.lower().endswith(".pdf")
        ]
        if no_pdf:
            raise serializers.ValidationError({
                "documentos": "Los documentos del expediente deben ser archivos PDF: " + ", ".join(no_pdf)
            })

        proforma = attrs.get("proforma")
        if proforma and not proforma.name.lower().endswith((".pdf", ".jpg", ".jpeg", ".png")):
            raise serializers.ValidationError({
                "proforma": "La cotización debe ser PDF, JPG, JPEG o PNG."
            })

        return attrs


class SolicitudCompraResumenSerializer(serializers.ModelSerializer):
    """Resumen liviano usado por Mantenimiento/Soporte para
    mostrar el estado de una compra vinculada sin exponer todos
    los campos ni requerir permiso de Compras."""

    estado_nombre = serializers.CharField(source="get_estado_display", read_only=True)
    documentos_pendientes = serializers.SerializerMethodField()

    def get_documentos_pendientes(self, obj):
        from .expediente import documentos_faltantes
        if obj.estado in ("CREADO_PENDIENTE_DAF", "EVALUADO_PENDIENTE_CERTIFICACION"):
            return documentos_faltantes(obj)
        return []

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for campo in ("informe", "proforma", "poa", "pedido"):
            if data.get(campo):
                data[campo] = urlsplit(data[campo]).path
        return firmar_urls(data, self.context.get('request'))

    class Meta:
        model = SolicitudCompra
        fields = [
            "id", "codigo", "titulo", "estado", "estado_nombre",
            "informe", "proforma", "poa", "pedido", "documentos_pendientes",
            "acta_conformidad", "fecha_entrega_solicitante",
            "cantidad_entregada", "entregado_a", "creado_en", "actualizado_en",
        ]
        read_only_fields = fields
