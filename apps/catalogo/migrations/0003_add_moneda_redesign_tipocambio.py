import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


def create_usd_and_migrate(apps, schema_editor):
    Moneda = apps.get_model('catalogo', 'Moneda')
    TipoCambio = apps.get_model('catalogo', 'TipoCambio')
    now = django.utils.timezone.now()
    usd = Moneda.objects.create(
        codigo='USD',
        nombre='Dólar americano',
        simbolo='$',
        activo=True,
        created_at=now,
        updated_at=now,
    )
    TipoCambio.objects.all().update(moneda=usd)


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0002_add_activo_to_categoria_condicion'),
    ]

    operations = [
        # 1. Crear modelo Moneda
        migrations.CreateModel(
            name='Moneda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('codigo', models.CharField(max_length=5, unique=True, verbose_name='Código')),
                ('nombre', models.CharField(max_length=100, verbose_name='Nombre')),
                ('simbolo', models.CharField(max_length=5, verbose_name='Símbolo')),
                ('activo', models.BooleanField(default=True, verbose_name='Activa')),
            ],
            options={
                'verbose_name': 'Moneda',
                'verbose_name_plural': 'Monedas',
                'ordering': ['codigo'],
            },
        ),
        # 2. Añadir FK nullable y campo nota
        migrations.AddField(
            model_name='tipocambio',
            name='moneda',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='tipos_cambio',
                to='catalogo.moneda',
                verbose_name='Moneda',
            ),
        ),
        migrations.AddField(
            model_name='tipocambio',
            name='nota',
            field=models.CharField(blank=True, max_length=200, verbose_name='Nota',
                                   help_text='Ej: Fuente SBS, ajuste por cierre de mes'),
        ),
        # 3. Data migration: crear USD y asignar a registros existentes
        migrations.RunPython(create_usd_and_migrate, migrations.RunPython.noop),
        # 4. Hacer moneda no-nullable
        migrations.AlterField(
            model_name='tipocambio',
            name='moneda',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='tipos_cambio',
                to='catalogo.moneda',
                verbose_name='Moneda',
            ),
        ),
        # 5. Quitar fecha
        migrations.RemoveField(
            model_name='tipocambio',
            name='fecha',
        ),
        # 6. Actualizar compra/venta a 4 decimales
        migrations.AlterField(
            model_name='tipocambio',
            name='compra',
            field=models.DecimalField(decimal_places=4, max_digits=10, verbose_name='Compra'),
        ),
        migrations.AlterField(
            model_name='tipocambio',
            name='venta',
            field=models.DecimalField(decimal_places=4, max_digits=10, verbose_name='Venta'),
        ),
        # 7. Actualizar opciones del modelo (ordering, quitar get_latest_by)
        migrations.AlterModelOptions(
            name='tipocambio',
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Tipo de cambio',
                'verbose_name_plural': 'Tipos de cambio',
            },
        ),
    ]
