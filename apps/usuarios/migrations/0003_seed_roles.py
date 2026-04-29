from django.db import migrations


MODULOS = ['clientes', 'catalogo', 'proformas', 'proyectos', 'usuarios', 'configuracion']

# (ver, crear, editar, eliminar) por modulo
PERMISOS_DEFAULT = {
    'admin': {m: (True, True, True, True) for m in MODULOS},
    'vendedor': {
        'clientes':       (True,  True,  True,  False),
        'catalogo':       (True,  False, False, False),
        'proformas':      (True,  True,  True,  False),
        'proyectos':      (True,  False, False, False),
        'usuarios':       (False, False, False, False),
        'configuracion':  (False, False, False, False),
    },
    'tecnico': {
        'clientes':       (True,  False, False, False),
        'catalogo':       (True,  False, False, False),
        'proformas':      (False, False, False, False),
        'proyectos':      (True,  False, False, False),
        'usuarios':       (False, False, False, False),
        'configuracion':  (False, False, False, False),
    },
    'auditor': {m: (True, False, False, False) for m in MODULOS},
    'cliente': {
        'clientes':       (False, False, False, False),
        'catalogo':       (False, False, False, False),
        'proformas':      (True,  False, False, False),
        'proyectos':      (True,  False, False, False),
        'usuarios':       (False, False, False, False),
        'configuracion':  (False, False, False, False),
    },
}

ROLES_CONFIG = [
    # (tipo, nombre, es_superadmin, color_badge)
    ('admin',    'Administrador', True,  'bg-purple-100 text-purple-800'),
    ('vendedor', 'Vendedor',      False, 'bg-blue-100 text-blue-800'),
    ('tecnico',  'Técnico',       False, 'bg-green-100 text-green-800'),
    ('auditor',  'Auditor',       False, 'bg-yellow-100 text-yellow-800'),
    ('cliente',  'Cliente',       False, 'bg-gray-100 text-gray-800'),
]


def seed_roles(apps, schema_editor):
    Rol = apps.get_model('usuarios', 'Rol')
    PermisoModulo = apps.get_model('usuarios', 'PermisoModulo')
    Usuario = apps.get_model('usuarios', 'Usuario')

    roles = {}
    for tipo, nombre, es_superadmin, color_badge in ROLES_CONFIG:
        rol = Rol.objects.create(
            nombre=nombre,
            tipo=tipo,
            es_superadmin=es_superadmin,
            color_badge=color_badge,
            activo=True,
        )
        roles[tipo] = rol

        for modulo, (ver, crear, editar, eliminar) in PERMISOS_DEFAULT[tipo].items():
            PermisoModulo.objects.create(
                rol=rol,
                modulo=modulo,
                puede_ver=ver,
                puede_crear=crear,
                puede_editar=editar,
                puede_eliminar=eliminar,
            )

    # Asignar rol FK a usuarios existentes según rol_legacy
    for usuario in Usuario.objects.all():
        tipo = getattr(usuario, 'rol_legacy', None) or 'vendedor'
        usuario.rol = roles.get(tipo, roles['vendedor'])
        usuario.save()


def unseed_roles(apps, schema_editor):
    Rol = apps.get_model('usuarios', 'Rol')
    Usuario = apps.get_model('usuarios', 'Usuario')
    Usuario.objects.all().update(rol=None)
    Rol.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_add_rol_models'),
    ]

    operations = [
        migrations.RunPython(seed_roles, unseed_roles),
        migrations.RemoveField(
            model_name='usuario',
            name='rol_legacy',
        ),
    ]
