import datetime
import decimal
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('clientes', '0003_add_activo_to_sede_contacto'),
        ('catalogo', '0003_add_moneda_redesign_tipocambio'),
    ]

    operations = [
        migrations.CreateModel(
            name='Proforma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('numero', models.CharField(db_index=True, max_length=20, verbose_name='Número')),
                ('version', models.PositiveSmallIntegerField(default=1, verbose_name='Versión')),
                ('es_vigente', models.BooleanField(default=True, verbose_name='Versión vigente')),
                ('titulo', models.CharField(max_length=300, verbose_name='Asunto')),
                ('estado', models.CharField(
                    choices=[
                        ('borrador', 'Borrador'),
                        ('enviada', 'Enviada'),
                        ('aprobada', 'Aprobada'),
                        ('rechazada', 'Rechazada'),
                        ('vencida', 'Vencida'),
                    ],
                    default='borrador',
                    max_length=20,
                    verbose_name='Estado',
                )),
                ('tc_venta', models.DecimalField(
                    blank=True, decimal_places=4, max_digits=10, null=True,
                    verbose_name='T.C. venta',
                    help_text='Valor snapshot al momento de crear la proforma',
                )),
                ('fecha_emision', models.DateField(default=datetime.date.today, verbose_name='Fecha de emisión')),
                ('validez_dias', models.PositiveSmallIntegerField(default=30, verbose_name='Validez (días)')),
                ('incluye_igv', models.BooleanField(default=True, verbose_name='Incluye IGV')),
                ('porcentaje_igv', models.DecimalField(
                    decimal_places=2, default=decimal.Decimal('18.00'), max_digits=5, verbose_name='% IGV',
                )),
                ('subtotal_usd', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Subtotal USD')),
                ('igv_usd', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='IGV USD')),
                ('total_usd', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Total USD')),
                ('subtotal_pen', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Subtotal PEN')),
                ('igv_pen', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='IGV PEN')),
                ('total_pen', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Total PEN')),
                ('observaciones', models.TextField(blank=True, verbose_name='Observaciones')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('empresa', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='proformas',
                    to='clientes.empresa',
                    verbose_name='Empresa',
                )),
                ('contacto', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='proformas',
                    to='clientes.contacto',
                    verbose_name='Contacto',
                )),
                ('sede', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='proformas',
                    to='clientes.sede',
                    verbose_name='Sede',
                )),
                ('tipo_cambio', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='proformas',
                    to='catalogo.tipocambio',
                    verbose_name='Tipo de cambio',
                )),
            ],
            options={
                'verbose_name': 'Proforma',
                'verbose_name_plural': 'Proformas',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='proforma',
            constraint=models.UniqueConstraint(fields=['numero', 'version'], name='unique_proforma_version'),
        ),
        migrations.CreateModel(
            name='ProformaItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orden', models.PositiveSmallIntegerField(default=0, verbose_name='Orden')),
                ('descripcion', models.CharField(max_length=300, verbose_name='Descripción')),
                ('descripcion_tecnica', models.TextField(blank=True, verbose_name='Descripción técnica')),
                ('unidad', models.CharField(
                    choices=[
                        ('servicio', 'Servicio'),
                        ('hora', 'Hora'),
                        ('punto', 'Punto'),
                        ('mes', 'Mes'),
                        ('dia', 'Día'),
                        ('km', 'Kilómetro'),
                        ('unidad', 'Unidad'),
                        ('global', 'Global'),
                    ],
                    default='servicio',
                    max_length=20,
                    verbose_name='Unidad',
                )),
                ('cantidad', models.DecimalField(decimal_places=2, default=1, max_digits=10, verbose_name='Cantidad')),
                ('precio_usd', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio USD')),
                ('proforma', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='items',
                    to='proformas.proforma',
                )),
                ('servicio', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='proforma_items',
                    to='catalogo.servicio',
                    verbose_name='Servicio del catálogo',
                )),
            ],
            options={
                'verbose_name': 'Ítem de proforma',
                'verbose_name_plural': 'Ítems de proforma',
                'ordering': ['orden', 'id'],
            },
        ),
        migrations.CreateModel(
            name='ProformaCondicion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orden', models.PositiveSmallIntegerField(default=0, verbose_name='Orden')),
                ('titulo', models.CharField(max_length=150, verbose_name='Título')),
                ('contenido', models.TextField(verbose_name='Contenido')),
                ('proforma', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='condiciones',
                    to='proformas.proforma',
                )),
                ('condicion_ref', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='proforma_condiciones',
                    to='catalogo.condicioncomercial',
                    verbose_name='Condición de catálogo',
                )),
            ],
            options={
                'verbose_name': 'Condición de proforma',
                'verbose_name_plural': 'Condiciones de proforma',
                'ordering': ['orden', 'id'],
            },
        ),
    ]
