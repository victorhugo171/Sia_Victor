from django.db import transaction
from django.conf import settings
from datetime import timedelta
from usuarios.archivos import firmar_urls
from django.utils import timezone

from rest_framework import serializers

from usuarios.models import Area, Usuario

from .models import (
    CategoriaTicket,
    EstadoTicket,
    Ticket,
    NotificacionSoporte,
    ESTADOS_TICKET_ACTIVOS_TECNICO,
)


class NotificacionSoporteSerializer(serializers.ModelSerializer):
    ticket_codigo = serializers.CharField(source="ticket.codigo", read_only=True)
    ticket_titulo = serializers.CharField(source="ticket.titulo", read_only=True)

    class Meta:
        model = NotificacionSoporte
        fields = ["id", "tipo", "titulo", "mensaje", "leida", "creada_en", "leida_en", "ticket", "ticket_codigo", "ticket_titulo"]
        read_only_fields = fields


# ==========================================================
# CATEGORÍA
# ==========================================================

class CategoriaTicketSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = CategoriaTicket

        fields = [
            "id",
            "codigo",
            "nombre",
            "descripcion",
            "activo",
        ]


# ==========================================================
# ESTADO
# ==========================================================

class EstadoTicketSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = EstadoTicket

        fields = [
            "id",
            "codigo",
            "nombre",
            "descripcion",
            "es_inicial",
            "es_terminal",
            "activo",
        ]


# ==========================================================
# TICKET SOPORTE TÉCNICO
# ==========================================================

class TicketSerializer(
    serializers.ModelSerializer
):

    # ======================================================
    # DATOS DESCRIPTIVOS PARA EL FRONTEND
    # ======================================================

    solicitante_nombre = serializers.CharField(
        source="solicitante.nombre_completo",
        read_only=True
    )

    solicitante_email = serializers.CharField(
        source="solicitante.email",
        read_only=True
    )

    tecnico_nombre = serializers.SerializerMethodField()

    area_nombre = serializers.CharField(
        source="area.nombre",
        read_only=True
    )

    categoria_nombre = serializers.CharField(
        source="categoria.nombre",
        read_only=True
    )

    categoria_codigo = serializers.CharField(
        source="categoria.codigo",
        read_only=True
    )

    estado_nombre = serializers.CharField(
        source="estado.nombre",
        read_only=True
    )

    estado_codigo = serializers.CharField(
        source="estado.codigo",
        read_only=True
    )

    especialistas_apoyo_nombres = (
        serializers.SerializerMethodField()
    )


    # ======================================================
    # CAMPOS QUE EL PORTAL SOLICITANTE YA NO PIDE
    # ======================================================
    #
    # El formulario simplificado del solicitante solo
    # captura título, descripción y foto. Estos campos
    # se completan con un valor por defecto en la vista
    # (TicketViewSet.create) cuando no llegan en el payload.
    # ======================================================

    area = serializers.PrimaryKeyRelatedField(
        queryset=Area.objects.all(),
        required=False
    )

    ubicacion = serializers.CharField(
        required=False,
        allow_blank=True
    )

    equipo_afectado = serializers.CharField(
        required=False,
        allow_blank=True
    )

    categoria = serializers.PrimaryKeyRelatedField(
        queryset=CategoriaTicket.objects.all(),
        required=False
    )

    prioridad = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True
    )

    estado = serializers.PrimaryKeyRelatedField(
        queryset=EstadoTicket.objects.all(),
        required=False
    )

    solucion = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    tecnico_asignado = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(),
        required=False,
        allow_null=True
    )

    fecha_limite = serializers.DateTimeField(
        source="sla_fecha_limite",
        required=False,
        allow_null=True
    )

    fecha_cierre = serializers.DateTimeField(
        source="cerrado_en",
        required=False,
        allow_null=True
    )

    vencido = serializers.BooleanField(
        read_only=True
    )


    # ======================================================
    # EVIDENCIA
    # ======================================================

    evidencia_archivo = serializers.FileField(
        required=False,
        allow_null=True
    )

    evidencia_archivo_url = (
        serializers.SerializerMethodField()
    )


    # ======================================================
    # DATOS CALCULADOS DEL SLA
    # ======================================================

    sla_estado = (
        serializers.SerializerMethodField()
    )

    sla_restante_minutos = (
        serializers.SerializerMethodField()
    )

    compra_vinculada = (
        serializers.SerializerMethodField()
    )

    cotizacion_archivo_url = (
        serializers.SerializerMethodField()
    )
    cotizaciones_requerimiento = serializers.SerializerMethodField()

    evidencia_diagnostico_url = serializers.SerializerMethodField()
    evidencia_intervencion_url = serializers.SerializerMethodField()
    evidencia_pruebas_url = serializers.SerializerMethodField()
    informe_final_pdf_url = serializers.SerializerMethodField()
    informe_tecnico_pdf_url = serializers.SerializerMethodField()
    informe_jefe_carrera_pdf_url = serializers.SerializerMethodField()


    # ======================================================
    # META
    # ======================================================

    def to_representation(self, instance):
        from urllib.parse import urlsplit
        data = super().to_representation(instance)
        for campo in ("informe_compra", "cotizacion_archivo"):
            if data.get(campo):
                data[campo] = urlsplit(data[campo]).path
        return firmar_urls(data, self.context.get('request'))

    class Meta:

        model = Ticket

        fields = [

            # ------------------------------------------------
            # IDENTIFICACIÓN
            # ------------------------------------------------

            "id",

            "codigo",

            "titulo",

            "descripcion",


            # ------------------------------------------------
            # SOLICITANTE
            # ------------------------------------------------

            "solicitante",

            "solicitante_nombre",

            "solicitante_email",


            # ------------------------------------------------
            # ÁREA / UBICACIÓN
            # ------------------------------------------------

            "area",

            "area_nombre",

            "ubicacion",

            "referencia_ubicacion",

            "equipo_afectado",


            # ------------------------------------------------
            # EVIDENCIA
            # ------------------------------------------------

            "evidencia",

            "evidencia_archivo",

            "evidencia_archivo_url",


            # ------------------------------------------------
            # CLASIFICACIÓN UTIC
            # ------------------------------------------------

            "categoria",

            "categoria_nombre",

            "categoria_codigo",

            "tipo_problema",

            "criterio_tecnico",


            # ------------------------------------------------
            # SLA
            # ------------------------------------------------

            "sla_horas",

            "sla_fecha_limite",

            "sla_cumplido",

            "sla_estado",

            "sla_restante_minutos",


            # ------------------------------------------------
            # ESTADO
            # ------------------------------------------------

            "estado",
            "fecha_limite",
            "fecha_cierre",
            "vencido",
            "solucion",

            "estado_nombre",

            "estado_codigo",


            # ------------------------------------------------
            # RESPONSABLES
            # ------------------------------------------------

            "tecnico_asignado",

            "tecnico_nombre",

            "especialistas_apoyo",

            "especialistas_apoyo_nombres",


            # ------------------------------------------------
            # DIAGNÓSTICO
            # ------------------------------------------------

            "diagnostico",

            "observaciones_diagnostico",

            "evidencia_diagnostico",

            "evidencia_diagnostico_url",

            "plan_solucion",

            "solucion",

            "acciones_realizadas",

            "componentes_utilizados",

            "evidencia_intervencion",

            "evidencia_intervencion_url",


            # ------------------------------------------------
            # COMPRA VINCULADA
            # ------------------------------------------------

            "requiere_compra",

            "cantidad_componente",

            "componente_requerido",

            "especificaciones_tecnicas",

            "justificacion_compra",

            "proveedor_cotizacion",

            "costo_estimado",

            "cotizacion_archivo", "informe_compra",

            "cotizacion_archivo_url",
            "cotizaciones_requerimiento",

            "estado_compra_componente",

            "motivo_no_viable",

            "componente_entregado_en",

            "codigo_compra_vinculada",

            "compra_vinculada",


            # ------------------------------------------------
            # RESULTADOS
            # ------------------------------------------------

            "resultado_pruebas",

            "evidencia_pruebas",

            "evidencia_pruebas_url",

            "conformidad_usuario",

            "observaciones_usuario",

            "informe_tecnico",
            "informe_tecnico_pdf",
            "informe_tecnico_pdf_url",
            "informe_jefe_carrera",
            "informe_jefe_carrera_pdf",
            "informe_jefe_carrera_pdf_url",
            "informe_jefe_carrera_en",

            "informe_final",

            "informe_final_pdf",

            "informe_final_pdf_url",

            "informe_elevado_en",

            "informe_recibido_director_en",

            "proceso_finalizado_en",


            # ------------------------------------------------
            # FECHAS DEL WORKFLOW
            # ------------------------------------------------

            "validado_en",

            "clasificado_en",

            "asignado_en",

            "inicio_atencion_en",

            "pruebas_en",

            "verificado_en",

            "conformidad_en",


            # ------------------------------------------------
            # CONTROL Y AUDITORÍA
            # ------------------------------------------------

            "rework_count",

            "activo",

            "creado_en",

            "actualizado_en",

            "cerrado_en",
        ]


        # ==================================================
        # CAMPOS CONTROLADOS POR SIGTA
        # ==================================================
        #
        # El solicitante NO puede enviar estos valores
        # directamente.
        #
        # Son modificados mediante las acciones específicas
        # definidas en soporte/views.py.
        #
        # ==================================================

        read_only_fields = [

            "codigo",

            "solicitante",

            "especialistas_apoyo",

            "tipo_problema",

            "criterio_tecnico",


            # SLA

            "sla_horas",

            "sla_fecha_limite",

            "sla_cumplido",


            # Diagnóstico

            "diagnostico",

            "observaciones_diagnostico",

            "evidencia_diagnostico",

            "plan_solucion",

            "solucion",

            "acciones_realizadas",

            "componentes_utilizados",

            "evidencia_intervencion",


            # Compra

            "requiere_compra",

            "cantidad_componente",

            "componente_requerido",

            "especificaciones_tecnicas",

            "justificacion_compra",

            "proveedor_cotizacion",

            "costo_estimado",

            "cotizacion_archivo", "informe_compra",

            "estado_compra_componente",

            "motivo_no_viable",

            "componente_entregado_en",

            "codigo_compra_vinculada",


            # Resultados

            "resultado_pruebas",

            "evidencia_pruebas",

            "conformidad_usuario",

            "observaciones_usuario",

            "informe_tecnico",

            "informe_final",

            "informe_elevado_en",

            "informe_recibido_director_en",

            "proceso_finalizado_en",


            # Fechas workflow

            "validado_en",

            "clasificado_en",

            "asignado_en",

            "inicio_atencion_en",

            "pruebas_en",

            "verificado_en",

            "conformidad_en",


            # Control

            "rework_count",

            "cerrado_en",

            "creado_en",

            "actualizado_en",
        ]


    # ======================================================
    # TÉCNICO ASIGNADO
    # ======================================================

    def get_tecnico_nombre(
        self,
        obj
    ):

        if not obj.tecnico_asignado:

            return None


        return (
            obj.tecnico_asignado
            .nombre_completo
        )


    # ======================================================
    # ESPECIALISTAS DE APOYO
    # ======================================================

    def get_especialistas_apoyo_nombres(
        self,
        obj
    ):

        return [
            usuario.nombre_completo

            for usuario
            in obj.especialistas_apoyo.all()
        ]


    # ======================================================
    # COMPRA VINCULADA (RESUMEN)
    # ======================================================

    def get_compra_vinculada(
        self,
        obj
    ):

        solicitud = (
            obj.compras_generadas
            .filter(activo=True)
            .order_by("-creado_en")
            .first()
        )

        if not solicitud:
            return None

        from compras.serializers import SolicitudCompraResumenSerializer

        return SolicitudCompraResumenSerializer(solicitud).data


    # ======================================================
    # URL DE LA COTIZACIÓN DEL COMPONENTE
    # ======================================================

    def _archivo_url(self, archivo):
        if not archivo:
            return None
        try:
            url = archivo.url
        except ValueError:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url

    def get_evidencia_diagnostico_url(self, obj):
        return self._archivo_url(obj.evidencia_diagnostico)

    def get_evidencia_intervencion_url(self, obj):
        return self._archivo_url(obj.evidencia_intervencion)

    def get_evidencia_pruebas_url(self, obj):
        return self._archivo_url(obj.evidencia_pruebas)

    def get_informe_final_pdf_url(self, obj):
        return self._archivo_url(obj.informe_final_pdf)

    def get_informe_tecnico_pdf_url(self, obj):
        return self._archivo_url(obj.informe_tecnico_pdf)

    def get_informe_jefe_carrera_pdf_url(self, obj):
        return self._archivo_url(obj.informe_jefe_carrera_pdf)

    def get_cotizacion_archivo_url(
        self,
        obj
    ):

        if not obj.cotizacion_archivo:

            return None


        try:

            url = obj.cotizacion_archivo.url

        except ValueError:

            return None


        request = self.context.get(
            "request"
        )


        return (
            request.build_absolute_uri(url)
            if request
            else url
        )

    def get_cotizaciones_requerimiento(self, obj):
        return [
            {
                "id": cotizacion.pk,
                "proveedor": cotizacion.proveedor,
                "documento_url": self._archivo_url(cotizacion.documento),
            }
            for cotizacion in obj.cotizaciones_requerimiento.all()
        ]


    # ======================================================
    # URL DEL ARCHIVO DE EVIDENCIA
    # ======================================================

    def get_evidencia_archivo_url(
        self,
        obj
    ):

        if not obj.evidencia_archivo:

            return None


        try:

            url = (
                obj.evidencia_archivo.url
            )

        except ValueError:

            return None


        request = self.context.get(
            "request"
        )


        if request:

            return (
                request.build_absolute_uri(
                    url
                )
            )


        return url


    # ======================================================
    # ESTADO DEL SLA
    # ======================================================

    def get_sla_estado(
        self,
        obj
    ):

        # --------------------------------------------------
        # TODAVÍA NO TIENE SLA
        # --------------------------------------------------

        if not obj.sla_fecha_limite:

            return "SIN_SLA"

        if obj.estado and obj.estado.codigo in ["RESUELTO", "CERRADO"]:
            return "CUMPLIDO" if obj.sla_cumplido is True else "INCUMPLIDO" if obj.sla_cumplido is False else "CERRADO"


        # --------------------------------------------------
        # TICKET CERRADO
        # --------------------------------------------------

        if obj.cerrado_en:

            if obj.sla_cumplido is True:

                return "CUMPLIDO"


            if obj.sla_cumplido is False:

                return "INCUMPLIDO"


        # --------------------------------------------------
        # TICKET ACTIVO
        # --------------------------------------------------

        ahora = timezone.now()


        if ahora > obj.sla_fecha_limite:

            return "VENCIDO"


        # --------------------------------------------------
        # CALCULAR RIESGO
        # --------------------------------------------------

        if obj.clasificado_en:

            duracion_total = (
                obj.sla_fecha_limite
                -
                obj.clasificado_en
            )

            tiempo_restante = (
                obj.sla_fecha_limite
                -
                ahora
            )


            # Menos del 25 % del SLA restante
            if (
                duracion_total.total_seconds()
                >
                0
            ):

                porcentaje_restante = (
                    tiempo_restante.total_seconds()
                    /
                    duracion_total.total_seconds()
                )


                if porcentaje_restante <= 0.25:

                    return "EN_RIESGO"


        return "EN_TIEMPO"


    # ======================================================
    # MINUTOS RESTANTES DEL SLA
    # ======================================================

    def get_sla_restante_minutos(
        self,
        obj
    ):

        if not obj.sla_fecha_limite:

            return None


        if obj.cerrado_en:

            return 0


        diferencia = (
            obj.sla_fecha_limite
            -
            timezone.now()
        )


        return int(
            diferencia.total_seconds()
            /
            60
        )


    # ======================================================
    # VALIDAR ARCHIVO DE EVIDENCIA
    # ======================================================

    def validate_evidencia_archivo(
        self,
        archivo
    ):

        if not archivo:

            return archivo


        # --------------------------------------------------
        # TAMAÑO MÁXIMO: 5 MB
        # --------------------------------------------------

        maximo = (
            5
            *
            1024
            *
            1024
        )


        if archivo.size > maximo:

            raise serializers.ValidationError(
                (
                    "El archivo no puede "
                    "superar los 5 MB."
                )
            )


        # --------------------------------------------------
        # EXTENSIONES
        # --------------------------------------------------

        nombre = (
            archivo.name
            .lower()
        )


        extensiones_permitidas = (
            ".jpg",
            ".jpeg",
            ".png",
            ".pdf",
        )


        if not nombre.endswith(
            extensiones_permitidas
        ):

            raise serializers.ValidationError(
                (
                    "Solo se permiten archivos "
                    "JPG, JPEG, PNG o PDF."
                )
            )


        return archivo


    # ======================================================
    # VALIDACIÓN GENERAL
    # ======================================================

    def validate(
        self,
        attrs
    ):

        # --------------------------------------------------
        # IMPORTANTE:
        #
        # En PATCH pueden no venir todos los campos.
        # Por eso utilizamos instance cuando exista.
        # --------------------------------------------------

        titulo = attrs.get(
            "titulo",
            getattr(
                self.instance,
                "titulo",
                ""
            )
        )


        descripcion = attrs.get(
            "descripcion",
            getattr(
                self.instance,
                "descripcion",
                ""
            )
        )


        ubicacion = attrs.get(
            "ubicacion",
            getattr(
                self.instance,
                "ubicacion",
                ""
            )
        )


        equipo = attrs.get(
            "equipo_afectado",
            getattr(
                self.instance,
                "equipo_afectado",
                ""
            )
        )


        # --------------------------------------------------
        # NORMALIZAR
        # --------------------------------------------------

        titulo = (
            str(
                titulo
                or
                ""
            )
            .strip()
        )


        descripcion = (
            str(
                descripcion
                or
                ""
            )
            .strip()
        )


        ubicacion = (
            str(
                ubicacion
                or
                ""
            )
            .strip()
        )


        equipo = (
            str(
                equipo
                or
                ""
            )
            .strip()
        )


        # ==================================================
        # REGLA 03: Prioridad alta automática por categoría
        # ==================================================
        cat = attrs.get('categoria')
        if cat is None and self.instance:
            cat = self.instance.categoria

        cat_code = ""
        if cat:
            if hasattr(cat, 'codigo'):
                cat_code = str(cat.codigo).upper()
            elif isinstance(cat, (int, str)):
                try:
                    c_obj = CategoriaTicket.objects.get(id=cat) if str(cat).isdigit() else CategoriaTicket.objects.get(codigo__iexact=str(cat))
                    cat_code = c_obj.codigo.upper()
                except Exception:
                    cat_code = str(cat).upper()

        cat_name = str(getattr(cat, 'nombre', '')).strip().upper() if cat else ''
        categorias_alta = {str(c).strip().upper() for c in settings.SIA_CATEGORIAS_PRIORIDAD_ALTA}
        equipo_normalizado = equipo.strip().upper()
        if (
            cat_code in categorias_alta
            or cat_name in categorias_alta
            or equipo_normalizado in categorias_alta
        ):
            attrs['prioridad'] = 'ALTA'

        # ==================================================
        # REGLA 05: Flujo de estados controlado
        # ==================================================
        nuevo_estado = attrs.get('estado')
        if self.instance and nuevo_estado and nuevo_estado != self.instance.estado:
            est_origen = self.instance.estado.codigo if self.instance.estado else None
            est_destino = nuevo_estado.codigo if hasattr(nuevo_estado, 'codigo') else str(nuevo_estado)

            if est_origen != est_destino:
                transiciones_validas = settings.SIA_TRANSICIONES_ESTADO
                destinos_posibles = transiciones_validas.get(est_origen, [])
                if est_destino not in destinos_posibles:
                    raise serializers.ValidationError({
                        "estado": f"Transición no permitida de {est_origen} a {est_destino}."
                    })

                # R05: EN_PROCESO -> RESUELTO requiere obligatorio un comentario/campo solucion
                if est_destino == 'RESUELTO':
                    sol = attrs.get('solucion') or getattr(self.instance, 'solucion', '') or attrs.get('diagnostico')
                    if not sol or not str(sol).strip():
                        raise serializers.ValidationError({
                            "solucion": "Debe especificar la solución para resolver el ticket."
                        })

                # R06: CERRADO -> EN_PROCESO (Reapertura dentro de 7 días solo por el solicitante)
                if est_origen == 'CERRADO' and est_destino == 'EN_PROCESO':
                    request = self.context.get('request')
                    if request and request.user != self.instance.solicitante:
                        raise serializers.ValidationError({
                            "detalle": "Solo el usuario solicitante puede reabrir el ticket."
                        })
                    fcierre = self.instance.fecha_cierre or self.instance.cerrado_en
                    dias_reapertura = settings.SIA_DIAS_REAPERTURA
                    if not fcierre:
                        raise serializers.ValidationError({"detalle": "No se puede reabrir el ticket porque no tiene fecha de cierre registrada."})
                    if (timezone.now() - fcierre).total_seconds() > dias_reapertura * 86400:
                        raise serializers.ValidationError({
                            "detalle": f"No se puede reabrir el ticket porque han pasado más de {dias_reapertura} días desde su cierre."
                        })

        # --------------------------------------------------
        # VALIDACIONES
        # --------------------------------------------------

        if not titulo:

            raise serializers.ValidationError(
                {
                    "titulo":
                        "El título es obligatorio."
                }
            )


        if not descripcion:

            raise serializers.ValidationError(
                {
                    "descripcion":
                        "La descripción es obligatoria."
                }
            )


        # --------------------------------------------------
        # UBICACIÓN Y EQUIPO AFECTADO
        #
        # El formulario simplificado del portal solicitante
        # ya no pide estos campos: TicketViewSet.create()
        # les asigna un valor por defecto cuando faltan.
        # Solo se exigen aquí en edición (self.instance ya
        # existe), donde el equipo interno sí los completa.
        # --------------------------------------------------

        if self.instance is not None:

            if not ubicacion:

                raise serializers.ValidationError(
                    {
                        "ubicacion":
                            "La ubicación es obligatoria."
                    }
                )


            if not equipo:

                raise serializers.ValidationError(
                    {
                        "equipo_afectado": (
                            "Debe indicar el equipo "
                            "afectado."
                        )
                    }
                )


        # ==================================================
        # REGLA 07: Máximo 5 tickets activos por técnico
        # ==================================================
        tecnico = attrs.get('tecnico_asignado')
        if tecnico and (not self.instance or tecnico.pk != self.instance.tecnico_asignado_id):
            with transaction.atomic():
                from usuarios.models import Usuario
                Usuario.objects.select_for_update().get(pk=tecnico.pk)
                activos_count = Ticket.objects.filter(
                    tecnico_asignado=tecnico,
                    estado__codigo__in=ESTADOS_TICKET_ACTIVOS_TECNICO
                )
                if self.instance and self.instance.pk:
                    activos_count = activos_count.exclude(pk=self.instance.pk)
                max_activos = settings.SIA_MAX_TICKETS_ACTIVOS_TECNICO
                if activos_count.count() >= max_activos:
                    raise serializers.ValidationError({
                        "tecnico_asignado": f"El especialista ya tiene {activos_count.count()} tareas activas. El límite es {max_activos}; seleccione otro especialista."
                    })

        if self.instance and attrs.get("estado"):
            destino = attrs["estado"].codigo
            if destino == "CERRADO" and not self.instance.cerrado_en:
                attrs["cerrado_en"] = timezone.now()

        return attrs

    def update(self, instance, validated_data):
        tecnico = validated_data.get("tecnico_asignado")
        if not tecnico or tecnico.pk == instance.tecnico_asignado_id:
            return super().update(instance, validated_data)

        from usuarios.models import Usuario
        max_activos = settings.SIA_MAX_TICKETS_ACTIVOS_TECNICO
        with transaction.atomic():
            Usuario.objects.select_for_update().get(pk=tecnico.pk)
            activos = Ticket.objects.filter(
                tecnico_asignado=tecnico,
                estado__codigo__in=ESTADOS_TICKET_ACTIVOS_TECNICO,
            ).exclude(pk=instance.pk)
            cantidad_activos = activos.count()
            if cantidad_activos >= max_activos:
                raise serializers.ValidationError({
                    "tecnico_asignado": f"El especialista ya tiene {cantidad_activos} tareas activas. El límite es {max_activos}; seleccione otro especialista."
                })
            return super().update(instance, validated_data)


    # ======================================================
    # CREAR TICKET
    # ======================================================

    def create(
        self,
        validated_data
    ):

        request = (
            self.context.get(
                "request"
            )
        )


        if not request:

            raise serializers.ValidationError(
                {
                    "detalle": (
                        "No se pudo identificar "
                        "al usuario."
                    )
                }
            )


        usuario = (
            request.user
        )


        # ==================================================
        # ESTADO INICIAL
        # ==================================================

        estado_nuevo = (
            EstadoTicket.objects.filter(codigo="NUEVO", activo=True).first()
            or EstadoTicket.objects.filter(codigo="ABIERTO", activo=True).first()
            or EstadoTicket.objects.filter(es_inicial=True, activo=True).first()
            or EstadoTicket.objects.first()
        )
        if not estado_nuevo:
            estado_nuevo = EstadoTicket.objects.create(codigo="NUEVO", nombre="Nuevo", es_inicial=True, activo=True)


        # ==================================================
        # GENERAR CÓDIGO
        # SOP-2026-0001
        # ==================================================

        anio = (
            timezone.now().year
        )


        prefijo = (
            f"SOP-{anio}-"
        )


        ultimo = (
            Ticket.objects
            .filter(
                codigo__startswith=prefijo
            )
            .order_by(
                "-codigo"
            )
            .first()
        )


        numero = 1


        if ultimo:

            try:

                numero = (
                    int(
                        ultimo.codigo
                        .split("-")[-1]
                    )
                    +
                    1
                )


            except (
                ValueError,
                IndexError
            ):

                numero = (
                    Ticket.objects
                    .filter(
                        codigo__startswith=prefijo
                    )
                    .count()
                    +
                    1
                )


        codigo = (
            f"{prefijo}{numero:04d}"
        )


        # ==================================================
        # CREAR
        # ==========================================================

        if "categoria" not in validated_data or not validated_data["categoria"]:
            validated_data["categoria"] = CategoriaTicket.objects.filter(activo=True).first()
        if "area" not in validated_data or not validated_data["area"]:
            from usuarios.models import Area
            validated_data["area"] = Area.objects.filter(activo=True).first()
        prioridad = validated_data.pop("prioridad", None)
        sla_horas = None
        sla_fecha_limite = None
        if prioridad:
            horas_map = settings.SIA_SLA_HORAS
            sla_horas = horas_map.get(str(prioridad).upper(), 24)
            try:
                from zoneinfo import ZoneInfo
                tz_lp = ZoneInfo("America/La_Paz")
            except Exception:
                import pytz
                tz_lp = pytz.timezone("America/La_Paz")
            ahora_lp = timezone.now().astimezone(tz_lp)
            sla_fecha_limite = ahora_lp + timedelta(hours=sla_horas)

        categoria = validated_data.get("categoria")
        if categoria is None and self.instance:
            categoria = self.instance.categoria
        categorias_alta = {str(c).strip().upper() for c in settings.SIA_CATEGORIAS_PRIORIDAD_ALTA}
        equipo_prioridad = str(validated_data.get("equipo_afectado", "")).strip().upper()
        if categoria and (
            str(categoria.codigo).strip().upper() in categorias_alta
            or str(categoria.nombre).strip().upper() in categorias_alta
        ) or equipo_prioridad in categorias_alta:
            prioridad = "ALTA"
            sla_horas = settings.SIA_SLA_HORAS["ALTA"]
            try:
                from zoneinfo import ZoneInfo
                tz_lp = ZoneInfo("America/La_Paz")
            except Exception:
                import pytz
                tz_lp = pytz.timezone("America/La_Paz")
            sla_fecha_limite = timezone.now().astimezone(tz_lp) + timedelta(hours=sla_horas)

        if prioridad == "ALTA" and sla_fecha_limite is None:
            try:
                from zoneinfo import ZoneInfo
                tz_lp = ZoneInfo("America/La_Paz")
            except Exception:
                import pytz
                tz_lp = pytz.timezone("America/La_Paz")
            sla_horas = settings.SIA_SLA_HORAS["ALTA"]
            sla_fecha_limite = timezone.now().astimezone(tz_lp) + timedelta(hours=sla_horas)

        if prioridad and not sla_fecha_limite:
            try:
                from zoneinfo import ZoneInfo
                tz_lp = ZoneInfo("America/La_Paz")
            except Exception:
                import pytz
                tz_lp = pytz.timezone("America/La_Paz")
            sla_horas = settings.SIA_SLA_HORAS.get(str(prioridad).upper(), settings.SIA_SLA_HORAS["MEDIA"])
            sla_fecha_limite = timezone.now().astimezone(tz_lp) + timedelta(hours=sla_horas)

        ticket = (
            Ticket.objects.create(

                codigo=codigo,

                solicitante=usuario,

                estado=estado_nuevo,

                # ==========================================
                # EL SOLICITANTE NO DEFINE:
                #
                # - prioridad
                # - SLA
                # - responsable
                # - estado
                #
                # ==========================================

                prioridad=prioridad,

                sla_horas=sla_horas,

                sla_fecha_limite=sla_fecha_limite,

                sla_cumplido=None,

                **validated_data
            )
        )


        return ticket
