from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('proyectos', '0001_initial'),
        ('clientes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlantillaDocumento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nombre', models.CharField(help_text='Ej: Contrato CCTV Estándar 2025, Adenda v2', max_length=150, verbose_name='Nombre')),
                ('tipo', models.CharField(
                    choices=[
                        ('contrato_servicios', 'Contrato de servicios'),
                        ('contrato_mantenimiento', 'Contrato de mantenimiento'),
                        ('contrato_software', 'Contrato de software'),
                        ('contrato_consultoria', 'Contrato de consultoría'),
                        ('nda', 'NDA / Confidencialidad'),
                        ('adenda', 'Adenda'),
                        ('acta_inicio', 'Acta de inicio'),
                        ('acta_entrega', 'Acta de entrega / Conformidad'),
                        ('orden_trabajo', 'Orden de trabajo'),
                        ('carta_garantia', 'Carta de garantía'),
                        ('carta_presentacion', 'Carta de presentación'),
                        ('informe_tecnico', 'Informe técnico'),
                        ('otro', 'Otro'),
                    ],
                    default='otro',
                    max_length=30,
                    verbose_name='Tipo',
                )),
                ('descripcion', models.CharField(blank=True, max_length=250, verbose_name='Descripción')),
                ('cuerpo_html', models.TextField(default='', help_text='Usa {{variable}} para datos automáticos al generar', verbose_name='Contenido')),
                ('es_predeterminada', models.BooleanField(default=False, verbose_name='Predeterminada para este tipo')),
                ('activo', models.BooleanField(default=True, verbose_name='Activa')),
                ('creado_por', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='plantillas_creadas',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Plantilla de documento',
                'verbose_name_plural': 'Plantillas de documentos',
                'ordering': ['tipo', 'nombre'],
            },
        ),
        migrations.CreateModel(
            name='DocumentoGenerado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nombre', models.CharField(max_length=200, verbose_name='Nombre del documento')),
                ('tipo', models.CharField(
                    choices=[
                        ('contrato_servicios', 'Contrato de servicios'),
                        ('contrato_mantenimiento', 'Contrato de mantenimiento'),
                        ('contrato_software', 'Contrato de software'),
                        ('contrato_consultoria', 'Contrato de consultoría'),
                        ('nda', 'NDA / Confidencialidad'),
                        ('adenda', 'Adenda'),
                        ('acta_inicio', 'Acta de inicio'),
                        ('acta_entrega', 'Acta de entrega / Conformidad'),
                        ('orden_trabajo', 'Orden de trabajo'),
                        ('carta_garantia', 'Carta de garantía'),
                        ('carta_presentacion', 'Carta de presentación'),
                        ('informe_tecnico', 'Informe técnico'),
                        ('otro', 'Otro'),
                    ],
                    default='otro',
                    max_length=30,
                    verbose_name='Tipo',
                )),
                ('cuerpo_html', models.TextField(verbose_name='Contenido editable')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('creado_por', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='documentos_generados',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('empresa', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='documentos_generados',
                    to='clientes.empresa',
                )),
                ('plantilla_origen', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='documentos_generados',
                    to='documentos.plantilladocumento',
                    verbose_name='Plantilla de origen',
                )),
                ('proyecto', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='documentos_generados',
                    to='proyectos.proyecto',
                )),
            ],
            options={
                'verbose_name': 'Documento generado',
                'verbose_name_plural': 'Documentos generados',
                'ordering': ['-created_at'],
            },
        ),
    ]
