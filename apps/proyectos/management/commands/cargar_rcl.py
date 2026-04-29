"""
Management command: carga los 3 proyectos del Real Club de Lima con sus actividades.
Uso: python manage.py cargar_rcl
"""
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.clientes.models import Empresa
from apps.proyectos.models import Actividad, ColumnaKanban, Proyecto


# ── Datos ────────────────────────────────────────────────────────────────────

EMPRESA_RCL = {
    'razon_social': 'Real Club de Lima',
    'ruc': '20100227837',
}

PROYECTOS = [
    {
        'titulo': 'Visor Web "Semáforo" (PWA) — Real Club de Lima',
        'estado': Proyecto.ESTADO_BORRADOR,
        'observaciones': 'Quick win. Aplicación satélite segura para vigilancia.',
        'duracion_dias': 10,
        'actividades': [
            {'codigo': 'S-01', 'titulo': 'Discovery Navasoft', 'grupo': '', 'prioridad': 'critica', 'dias': 2},
            {'codigo': 'S-02', 'titulo': 'Configuración SQL Read-Only', 'grupo': '', 'prioridad': 'critica', 'dias': 1},
            {'codigo': 'S-03', 'titulo': 'Setup proyecto PWA', 'grupo': '', 'prioridad': 'media', 'dias': 1},
            {'codigo': 'S-04', 'titulo': 'Endpoint de validación de socio', 'grupo': '', 'prioridad': 'alta', 'dias': 2},
            {'codigo': 'S-05', 'titulo': 'Lógica de reglas de negocio (estados)', 'grupo': '', 'prioridad': 'alta', 'dias': 1},
            {'codigo': 'S-06', 'titulo': 'UI Semáforo', 'grupo': '', 'prioridad': 'media', 'dias': 2},
            {'codigo': 'S-07', 'titulo': 'Integración de fotos', 'grupo': '', 'prioridad': 'media', 'dias': 1},
            {'codigo': 'S-08', 'titulo': 'Autenticación de vigilantes', 'grupo': '', 'prioridad': 'alta', 'dias': 1},
            {'codigo': 'S-09', 'titulo': 'Auditoría de consultas (LPDP)', 'grupo': '', 'prioridad': 'critica', 'dias': 1},
            {'codigo': 'S-10', 'titulo': 'QA en sedes', 'grupo': '', 'prioridad': 'media', 'dias': 1},
            {'codigo': 'S-11', 'titulo': 'Documentación y manual', 'grupo': '', 'prioridad': 'baja', 'dias': 1},
        ],
    },
    {
        'titulo': 'Reingeniería y Migración de Intranet — Real Club de Lima',
        'estado': Proyecto.ESTADO_BORRADOR,
        'observaciones': 'Migrar intranet PHP/MySQL a stack moderno con LPDP.',
        'duracion_dias': 58,
        'actividades': [
            # A — Fundación técnica
            {'codigo': 'I-01', 'titulo': 'Decisión de stack', 'grupo': 'Fundación técnica', 'prioridad': 'alta', 'dias': 1},
            {'codigo': 'I-02', 'titulo': 'Setup repo Git y CI/CD', 'grupo': 'Fundación técnica', 'prioridad': 'media', 'dias': 2},
            {'codigo': 'I-03', 'titulo': 'Arquitectura limpia', 'grupo': 'Fundación técnica', 'prioridad': 'alta', 'dias': 2},
            {'codigo': 'I-04', 'titulo': 'Diseño de nuevo esquema BD + script de migración', 'grupo': 'Fundación técnica', 'prioridad': 'critica', 'dias': 3},
            {'codigo': 'I-05', 'titulo': 'Setup framework frontend', 'grupo': 'Fundación técnica', 'prioridad': 'media', 'dias': 2},
            {'codigo': 'I-06', 'titulo': 'Documentación técnica viva', 'grupo': 'Fundación técnica', 'prioridad': 'baja', 'dias': 1},
            # B — Seguridad y autenticación
            {'codigo': 'I-07', 'titulo': 'Módulo Auth con JWT', 'grupo': 'Seguridad y autenticación', 'prioridad': 'alta', 'dias': 2},
            {'codigo': 'I-08', 'titulo': 'Implementación 2FA', 'grupo': 'Seguridad y autenticación', 'prioridad': 'alta', 'dias': 2},
            {'codigo': 'I-09', 'titulo': 'Sistema de roles y permisos', 'grupo': 'Seguridad y autenticación', 'prioridad': 'media', 'dias': 2},
            {'codigo': 'I-10', 'titulo': 'Recuperación de contraseña', 'grupo': 'Seguridad y autenticación', 'prioridad': 'media', 'dias': 2},
            # C — Migración de módulos
            {'codigo': 'I-11', 'titulo': 'Dashboard del socio', 'grupo': 'Migración de módulos', 'prioridad': 'media', 'dias': 3},
            {'codigo': 'I-12', 'titulo': 'Módulo Reservas (mesas/sillas)', 'grupo': 'Migración de módulos', 'prioridad': 'alta', 'dias': 6},
            {'codigo': 'I-13', 'titulo': 'Módulo Talleres', 'grupo': 'Migración de módulos', 'prioridad': 'media', 'dias': 3},
            {'codigo': 'I-14', 'titulo': 'Módulo Check-in/Check-out', 'grupo': 'Migración de módulos', 'prioridad': 'media', 'dias': 3},
            {'codigo': 'I-15', 'titulo': 'Pago Estado de Cuenta (Niubiz + Navasoft)', 'grupo': 'Migración de módulos', 'prioridad': 'critica', 'dias': 5},
            {'codigo': 'I-16', 'titulo': 'Módulo HelpDesk', 'grupo': 'Migración de módulos', 'prioridad': 'media', 'dias': 3},
            {'codigo': 'I-17', 'titulo': 'Módulo Documentos / Biblioteca', 'grupo': 'Migración de módulos', 'prioridad': 'media', 'dias': 2},
            {'codigo': 'I-18', 'titulo': 'Panel administrativo', 'grupo': 'Migración de módulos', 'prioridad': 'media', 'dias': 4},
            # D — Cumplimiento LPDP
            {'codigo': 'I-19', 'titulo': 'Pantalla de consentimiento expreso', 'grupo': 'Cumplimiento LPDP', 'prioridad': 'critica', 'dias': 2},
            {'codigo': 'I-20', 'titulo': 'Panel de Derechos ARCO', 'grupo': 'Cumplimiento LPDP', 'prioridad': 'critica', 'dias': 3},
            {'codigo': 'I-21', 'titulo': 'Tablas de auditoría + middleware', 'grupo': 'Cumplimiento LPDP', 'prioridad': 'critica', 'dias': 2},
            {'codigo': 'I-22', 'titulo': 'Aviso de privacidad y banner de cookies', 'grupo': 'Cumplimiento LPDP', 'prioridad': 'media', 'dias': 1},
            # E — UI/UX, QA y despliegue
            {'codigo': 'I-23', 'titulo': 'Diseño responsive completo', 'grupo': 'QA y despliegue', 'prioridad': 'media', 'dias': 3},
            {'codigo': 'I-24', 'titulo': 'Pruebas unitarias módulos críticos', 'grupo': 'QA y despliegue', 'prioridad': 'media', 'dias': 2},
            {'codigo': 'I-25', 'titulo': 'Pruebas de regresión Niubiz', 'grupo': 'QA y despliegue', 'prioridad': 'critica', 'dias': 1},
            {'codigo': 'I-26', 'titulo': 'Plan de cutover y migración productiva', 'grupo': 'QA y despliegue', 'prioridad': 'critica', 'dias': 1},
            {'codigo': 'I-27', 'titulo': 'Capacitación al equipo', 'grupo': 'QA y despliegue', 'prioridad': 'baja', 'dias': 1},
        ],
    },
    {
        'titulo': 'Servicio DBA (Encriptación + Auditoría) — Real Club de Lima',
        'estado': Proyecto.ESTADO_BORRADOR,
        'observaciones': 'Hardening SQL Server, TDE, auditoría y restricción de privilegios.',
        'duracion_dias': 9,
        'actividades': [
            {'codigo': 'D-01', 'titulo': 'Reunión de scoping con Katiuska', 'grupo': '', 'prioridad': 'critica', 'dias': 1},
            {'codigo': 'D-02', 'titulo': 'Inventario de seguridad actual', 'grupo': '', 'prioridad': 'media', 'dias': 1},
            {'codigo': 'D-03', 'titulo': 'Configuración TDE', 'grupo': '', 'prioridad': 'critica', 'dias': 2},
            {'codigo': 'D-04', 'titulo': 'Backup seguro de certificados', 'grupo': '', 'prioridad': 'critica', 'dias': 1},
            {'codigo': 'D-05', 'titulo': 'SQL Server Audit', 'grupo': '', 'prioridad': 'alta', 'dias': 2},
            {'codigo': 'D-06', 'titulo': 'Hardening de privilegios', 'grupo': '', 'prioridad': 'critica', 'dias': 2},
            {'codigo': 'D-07', 'titulo': 'Política de credenciales', 'grupo': '', 'prioridad': 'media', 'dias': 1},
            {'codigo': 'D-08', 'titulo': 'Documentación técnica final', 'grupo': '', 'prioridad': 'critica', 'dias': 1},
        ],
    },
]


class Command(BaseCommand):
    help = 'Carga los 3 proyectos del Real Club de Lima con sus actividades'

    def handle(self, *args, **options):
        empresa, _ = Empresa.objects.get_or_create(
            ruc=EMPRESA_RCL['ruc'],
            defaults={'razon_social': EMPRESA_RCL['razon_social']},
        )
        self.stdout.write(f'Empresa: {empresa}')

        for proy_data in PROYECTOS:
            existing = Proyecto.objects.filter(
                empresa=empresa, titulo=proy_data['titulo'], activo=True,
            ).first()
            if existing:
                self.stdout.write(f'  Ya existe: {existing.numero} - {existing.titulo}')
                continue

            numero = Proyecto.generar_numero()
            proyecto = Proyecto.objects.create(
                numero=numero,
                empresa=empresa,
                titulo=proy_data['titulo'],
                estado=proy_data['estado'],
                observaciones=proy_data['observaciones'],
                valor_usd=Decimal('0'),
                valor_pen=Decimal('0'),
            )
            ColumnaKanban.crear_defaults(proyecto)
            self.stdout.write(f'  Proyecto creado: {proyecto.numero} - {proyecto.titulo}')

            for idx, act_data in enumerate(proy_data['actividades']):
                Actividad.objects.create(
                    proyecto=proyecto,
                    grupo=act_data['grupo'],
                    titulo=f"[{act_data['codigo']}] {act_data['titulo']}",
                    descripcion='',
                    estado=Actividad.ESTADO_PENDIENTE,
                    prioridad=act_data['prioridad'],
                    orden=idx,
                )

            self.stdout.write(
                self.style.SUCCESS(f'    > {len(proy_data["actividades"])} actividades cargadas')
            )

        self.stdout.write(self.style.SUCCESS('\nCarga completada.'))
