from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0004_add_producto_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicio',
            name='costo',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Costo interno / lo que cobra el proveedor. Opcional.', max_digits=10, null=True, verbose_name='Costo Gibit'),
        ),
        migrations.AddField(
            model_name='servicio',
            name='moneda_costo',
            field=models.CharField(choices=[('USD', 'USD'), ('PEN', 'S/')], default='USD', max_length=5, verbose_name='Moneda del costo'),
        ),
        migrations.AddField(
            model_name='producto',
            name='costo',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Costo de compra / proveedor. Opcional.', max_digits=10, null=True, verbose_name='Costo Gibit'),
        ),
        migrations.AddField(
            model_name='producto',
            name='moneda_costo',
            field=models.CharField(choices=[('USD', 'USD'), ('PEN', 'S/')], default='USD', max_length=5, verbose_name='Moneda del costo'),
        ),
    ]
