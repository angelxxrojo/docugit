from django.db import migrations, models
import django.db.models.deletion


def seed_columnas(apps, schema_editor):
    Proyecto      = apps.get_model('proyectos', 'Proyecto')
    ColumnaKanban = apps.get_model('proyectos', 'ColumnaKanban')
    defaults = [
        ('Pendiente',   'pendiente',   0, 'gray',  False),
        ('En progreso', 'en_progreso', 1, 'blue',  False),
        ('En revisión', 'en_revision', 2, 'amber', False),
        ('Completado',  'completado',  3, 'green', True),
    ]
    for proyecto in Proyecto.objects.all():
        for nombre, slug, orden, color, es_final in defaults:
            ColumnaKanban.objects.get_or_create(
                proyecto=proyecto, slug=slug,
                defaults={'nombre': nombre, 'orden': orden, 'color': color, 'es_final': es_final},
            )


class Migration(migrations.Migration):

    dependencies = [
        ('proyectos', '0005_registro_tiempo'),
    ]

    operations = [
        migrations.CreateModel(
            name='ColumnaKanban',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nombre',   models.CharField(max_length=50, verbose_name='Nombre')),
                ('slug',     models.CharField(max_length=50, verbose_name='Slug')),
                ('orden',    models.PositiveSmallIntegerField(default=0, verbose_name='Orden')),
                ('color',    models.CharField(
                    choices=[
                        ('gray', 'Gris'), ('blue', 'Azul'), ('amber', 'Ámbar'),
                        ('green', 'Verde'), ('red', 'Rojo'), ('purple', 'Púrpura'),
                        ('indigo', 'Índigo'), ('pink', 'Rosa'),
                    ],
                    default='gray', max_length=20, verbose_name='Color',
                )),
                ('es_final', models.BooleanField(default=False, verbose_name='Es estado final')),
                ('activo',   models.BooleanField(default=True, verbose_name='Activa')),
                ('proyecto', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='columnas_kanban',
                    to='proyectos.proyecto',
                )),
            ],
            options={
                'verbose_name': 'Columna Kanban',
                'verbose_name_plural': 'Columnas Kanban',
                'ordering': ['orden'],
                'default_permissions': (),
            },
        ),
        migrations.AddConstraint(
            model_name='columnakanban',
            constraint=models.UniqueConstraint(fields=['proyecto', 'slug'], name='unique_columna_proyecto_slug'),
        ),
        migrations.RunPython(seed_columnas, migrations.RunPython.noop),
        # Actividad.estado ya no tiene choices fijas — cualquier slug es válido
        migrations.AlterField(
            model_name='actividad',
            name='estado',
            field=models.CharField(default='pendiente', max_length=50, verbose_name='Estado'),
        ),
    ]
