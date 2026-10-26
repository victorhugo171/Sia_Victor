from django.apps import AppConfig
from django.db.models.signals import post_migrate


def inicializar_estados_soporte(sender, **kwargs):
    try:
        from soporte.models import EstadoTicket, CategoriaTicket
        estados = [
            ('ABIERTO', 'Abierto', True, False),
            ('EN_PROCESO', 'En proceso', False, False),
            ('RESUELTO', 'Resuelto', False, False),
            ('CERRADO', 'Cerrado', False, True),
        ]
        for cod, nom, ini, term in estados:
            EstadoTicket.objects.get_or_create(codigo=cod, defaults={'nombre': nom, 'es_inicial': ini, 'es_terminal': term, 'activo': True})

        cats = [
            ('RED', 'Redes y conectividad'),
            ('SERVIDORES', 'Servidores'),
        ]
        for cod, nom in cats:
            CategoriaTicket.objects.get_or_create(codigo=cod, defaults={'nombre': nom, 'activo': True})
    except Exception:
        pass


class SoporteConfig(AppConfig):
    name = 'soporte'

    def ready(self):
        post_migrate.connect(inicializar_estados_soporte, sender=self)
