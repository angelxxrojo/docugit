import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('clientes', '0003_add_activo_to_sede_contacto'),
        ('proformas', '0002_add_producto_to_proformaitem'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Proyecto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('numero', models.CharField(db_index=True, max_length=20, unique=True, verbose_name='Número')),
                ('titulo', models.CharField(max_length=300, verbose_name='Título / Alcance')),
                ('estado', models.CharField(
                    choices=[
                        ('borrador', 'Borrador'),
                        ('pendiente_firma', 'Pendiente de firma'),
                        ('activo', 'Activo'),
                        ('en_ejecucion', 'En ejecución'),
                        ('completado', 'Completado'),
                        ('cancelado', 'Cancelado'),
                    ],
                    default='borrador', max_length=20, verbose_name='Estado',
                )),
                ('fecha_inicio', models.DateField(blank=True, null=True, verbose_name='Fecha de inicio')),
                ('fecha_fin_prevista', models.DateField(blank=True, null=True, verbose_name='Fecha fin prevista')),
                ('fecha_fin_real', models.DateField(blank=True, null=True, verbose_name='Fecha fin real')),
                ('valor_usd', models.DecimalField(
                    decimal_places=2, default=0, max_digits=14, verbose_name='Valor (USD)',
                )),
                ('valor_pen', models.DecimalField(
                    decimal_places=2, default=0, max_digits=14, verbose_name='Valor (PEN)',
                )),
                ('tc_venta', models.DecimalField(
                    blank=True, decimal_places=4, max_digits=10, null=True,
                    verbose_name='T.C. venta',
                    help_text='Tipo de cambio al momento de crear el proyecto',
                )),
                ('observaciones', models.TextField(blank=True, verbose_name='Observaciones')),
                ('texto_contrato', models.TextField(
                    blank=True, verbose_name='Texto del contrato',
                    help_text='Cláusulas y condiciones adicionales para el contrato imprimible',
                )),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('empresa', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='proyectos', to='clientes.empresa', verbose_name='Empresa',
                )),
                ('contacto', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='proyectos', to='clientes.contacto', verbose_name='Contacto',
                )),
                ('sede', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='proyectos', to='clientes.sede', verbose_name='Sede',
                )),
                ('proforma', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='proyectos', to='proformas.proforma',
                    verbose_name='Proforma origen',
                )),
            ],
            options={
                'verbose_name': 'Proyecto',
                'verbose_name_plural': 'Proyectos',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TecnicoAsignado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proyecto', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='tecnicos', to='proyectos.proyecto',
                )),
                ('tecnico', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='proyectos_asignados',
                    to=settings.AUTH_USER_MODEL, verbose_name='Técnico',
                )),
            ],
            options={
                'verbose_name': 'Técnico asignado',
                'verbose_name_plural': 'Técnicos asignados',
                'ordering': ['tecnico__first_name', 'tecnico__last_name'],
            },
        ),
        migrations.AddConstraint(
            model_name='tecnicoasignado',
            constraint=models.UniqueConstraint(
                fields=['proyecto', 'tecnico'], name='unique_tecnico_proyecto',
            ),
        ),
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tipo', models.CharField(
                    choices=[
                        ('contrato_firmado', 'Contrato firmado'),
                        ('sctr', 'SCTR técnico'),
                        ('addendum', 'Adenda / Addendum'),
                        ('acta_entrega', 'Acta de entrega'),
                        ('factura', 'Factura'),
                        ('otro', 'Otro'),
                    ],
                    default='otro', max_length=20, verbose_name='Tipo',
                )),
                ('titulo', models.CharField(max_length=200, verbose_name='Título')),
                ('archivo', models.FileField(upload_to='proyectos/documentos/%Y/%m/', verbose_name='Archivo')),
                ('fecha_vencimiento', models.DateField(
                    blank=True, null=True, verbose_name='Fecha de vencimiento',
                    help_text='Solo para SCTR. Si vence, bloquea inicio de ejecución',
                )),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('proyecto', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='documentos', to='proyectos.proyecto',
                )),
                ('tecnico', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='sctr_documentos',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Técnico (SCTR)',
                    help_text='Solo para documentos SCTR',
                )),
            ],
            options={
                'verbose_name': 'Documento',
                'verbose_name_plural': 'Documentos',
                'ordering': ['-created_at'],
            },
        ),
    ]
