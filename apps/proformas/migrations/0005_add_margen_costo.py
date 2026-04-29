from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proformas', '0004_remove_proforma_unique_proforma_version_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='proforma',
            name='margen_objetivo',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), help_text='% de ganancia que se aplicará al calcular precios sugeridos', max_digits=5, verbose_name='Margen objetivo (%)'),
        ),
        migrations.AddField(
            model_name='proformaitem',
            name='costo',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Costo Gibit'),
        ),
        migrations.AddField(
            model_name='proformaitem',
            name='moneda_costo',
            field=models.CharField(choices=[('USD', 'USD'), ('PEN', 'S/')], default='USD', max_length=5, verbose_name='Moneda del costo'),
        ),
    ]
