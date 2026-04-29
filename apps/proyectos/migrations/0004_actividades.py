from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proyectos', '0003_alter_proyecto_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='proyecto',
            options={
                'default_permissions': (),
                'ordering': ['-created_at'],
                'permissions': [
                    ('ver_proyectos',         'Ver lista de proyectos'),
                    ('crear_proyecto',        'Crear proyecto'),
                    ('editar_proyecto',       'Editar proyecto'),
                    ('eliminar_proyecto',     'Archivar proyecto'),
                    ('ver_actividades',       'Ver actividades / Kanban'),
                    ('gestionar_actividades', 'Crear y editar actividades'),
                ],
                'verbose_name': 'Proyecto',
                'verbose_name_plural': 'Proyectos',
            },
        ),
        migrations.CreateModel(
            name='Actividad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('titulo', models.CharField(max_length=200, verbose_name='Título')),
                ('descripcion', models.TextField(blank=True, verbose_name='Descripción')),
                ('estado', models.CharField(
                    choices=[
                        ('pendiente', 'Pendiente'),
                        ('en_progreso', 'En progreso'),
                        ('en_revision', 'En revisión'),
                        ('completado', 'Completado'),
                        ('cancelado', 'Cancelado'),
                    ],
                    default='pendiente', max_length=20, verbose_name='Estado',
                )),
                ('prioridad', models.CharField(
                    choices=[
                        ('baja', 'Baja'),
                        ('media', 'Media'),
                        ('alta', 'Alta'),
                        ('critica', 'Crítica'),
                    ],
                    default='media', max_length=10, verbose_name='Prioridad',
                )),
                ('fecha_inicio', models.DateField(blank=True, null=True, verbose_name='Fecha inicio')),
                ('fecha_vencimiento', models.DateField(blank=True, null=True, verbose_name='Fecha vencimiento')),
                ('progreso', models.PositiveSmallIntegerField(default=0, verbose_name='Progreso (%)')),
                ('orden', models.PositiveIntegerField(db_index=True, default=0, verbose_name='Orden')),
                ('activo', models.BooleanField(default=True, verbose_name='Activa')),
                ('proyecto', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='actividades',
                    to='proyectos.proyecto',
                )),
                ('responsable', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='actividades_asignadas',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Responsable',
                )),
            ],
            options={
                'verbose_name': 'Actividad',
                'verbose_name_plural': 'Actividades',
                'ordering': ['orden', 'created_at'],
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ComentarioActividad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('texto', models.TextField(verbose_name='Comentario')),
                ('actividad', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='comentarios',
                    to='proyectos.actividad',
                )),
                ('autor', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Comentario',
                'ordering': ['created_at'],
            },
        ),
    ]
