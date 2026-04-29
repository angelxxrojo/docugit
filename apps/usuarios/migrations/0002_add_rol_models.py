import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        # ── Crear tabla Rol ───────────────────────────────────────────────────
        migrations.CreateModel(
            name='Rol',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nombre', models.CharField(max_length=50, unique=True, verbose_name='Nombre')),
                ('tipo', models.CharField(
                    choices=[
                        ('admin', 'Administrador'), ('vendedor', 'Vendedor'),
                        ('tecnico', 'Técnico'), ('auditor', 'Auditor'),
                        ('cliente', 'Cliente'), ('custom', 'Personalizado'),
                    ],
                    default='custom', max_length=20, verbose_name='Tipo base',
                )),
                ('descripcion', models.CharField(blank=True, max_length=200, verbose_name='Descripción')),
                ('color_badge', models.CharField(
                    default='bg-gray-100 text-gray-800', max_length=80, verbose_name='Color',
                )),
                ('es_superadmin', models.BooleanField(default=False, verbose_name='Acceso total')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
            ],
            options={
                'verbose_name': 'Rol',
                'verbose_name_plural': 'Roles',
                'ordering': ['nombre'],
            },
        ),
        # ── Crear tabla PermisoModulo ─────────────────────────────────────────
        migrations.CreateModel(
            name='PermisoModulo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rol', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='permisos', to='usuarios.rol', verbose_name='Rol',
                )),
                ('modulo', models.CharField(
                    choices=[
                        ('clientes', 'Clientes / CRM'), ('catalogo', 'Catálogo'),
                        ('proformas', 'Proformas'), ('proyectos', 'Proyectos'),
                        ('usuarios', 'Usuarios'), ('configuracion', 'Configuración'),
                    ],
                    max_length=20, verbose_name='Módulo',
                )),
                ('puede_ver', models.BooleanField(default=True, verbose_name='Ver')),
                ('puede_crear', models.BooleanField(default=False, verbose_name='Crear')),
                ('puede_editar', models.BooleanField(default=False, verbose_name='Editar')),
                ('puede_eliminar', models.BooleanField(default=False, verbose_name='Eliminar')),
            ],
            options={
                'verbose_name': 'Permiso de módulo',
                'verbose_name_plural': 'Permisos de módulo',
                'ordering': ['modulo'],
                'unique_together': {('rol', 'modulo')},
            },
        ),
        # ── Añadir foto a Usuario ─────────────────────────────────────────────
        migrations.AddField(
            model_name='usuario',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to='usuarios/fotos/', verbose_name='Foto de perfil'),
        ),
        # ── Renombrar campo rol (CharField) a rol_legacy ──────────────────────
        migrations.RenameField(
            model_name='usuario',
            old_name='rol',
            new_name='rol_legacy',
        ),
        # ── Añadir nuevo campo rol (FK a Rol) ─────────────────────────────────
        migrations.AddField(
            model_name='usuario',
            name='rol',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='usuarios', to='usuarios.rol', verbose_name='Rol',
            ),
        ),
    ]
