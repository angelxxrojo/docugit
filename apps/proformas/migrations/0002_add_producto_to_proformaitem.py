import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proformas', '0001_initial'),
        ('catalogo', '0004_add_producto_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='proformaitem',
            name='producto',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='proforma_items',
                to='catalogo.producto',
                verbose_name='Producto del catálogo',
            ),
        ),
    ]
