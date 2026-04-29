from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import apps.documentos.models


class Migration(migrations.Migration):

    dependencies = [
        ('documentos', '0002_alter_plantilladocumento_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='plantilladocumento',
            options={
                'default_permissions': (),
                'ordering': ['tipo', 'nombre'],
                'permissions': [
                    ('ver_documentos', 'Ver documentos generados'),
                    ('crear_documento', 'Crear documento'),
                    ('editar_documento', 'Editar documento'),
                    ('eliminar_documento', 'Archivar documento'),
                    ('gestionar_plantillas', 'Gestionar plantillas de documentos'),
                    ('gestionar_repositorio', 'Gestionar repositorio de archivos'),
                ],
                'verbose_name': 'Plantilla de documento',
                'verbose_name_plural': 'Plantillas de documentos',
            },
        ),
        migrations.CreateModel(
            name='CarpetaRepositorio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
                ('descripcion', models.CharField(blank=True, max_length=250, verbose_name='Descripción')),
                ('activo', models.BooleanField(default=True, verbose_name='Activa')),
                ('carpeta_padre', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='subcarpetas',
                    to='documentos.carpetarepositorio',
                    verbose_name='Carpeta padre',
                )),
                ('creado_por', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Carpeta de repositorio',
                'verbose_name_plural': 'Carpetas de repositorio',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='ArchivoRepositorio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nombre', models.CharField(max_length=200, verbose_name='Nombre')),
                ('descripcion', models.CharField(blank=True, max_length=250, verbose_name='Descripción')),
                ('archivo', models.FileField(upload_to=apps.documentos.models._repositorio_upload, verbose_name='Archivo')),
                ('tamano_bytes', models.PositiveIntegerField(default=0, verbose_name='Tamaño (bytes)')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('carpeta', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='archivos',
                    to='documentos.carpetarepositorio',
                    verbose_name='Carpeta',
                )),
                ('subido_por', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Archivo de repositorio',
                'verbose_name_plural': 'Archivos de repositorio',
                'ordering': ['nombre'],
            },
        ),
    ]
