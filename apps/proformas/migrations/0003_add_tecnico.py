import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proformas', '0002_add_producto_to_proformaitem'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='proforma',
            name='tecnico',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='proformas_preparadas',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Técnico / Responsable',
            ),
        ),
    ]
