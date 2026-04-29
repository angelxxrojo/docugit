import datetime

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proyectos', '0004_actividades'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistroTiempo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('fecha', models.DateField(default=datetime.date.today, verbose_name='Fecha')),
                ('horas', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Horas')),
                ('descripcion', models.TextField(blank=True, verbose_name='Descripción')),
                ('actividad', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='registros_tiempo',
                    to='proyectos.actividad',
                    verbose_name='Actividad',
                )),
                ('usuario', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='registros_tiempo',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Usuario',
                )),
            ],
            options={
                'verbose_name': 'Registro de tiempo',
                'verbose_name_plural': 'Registros de tiempo',
                'ordering': ['-fecha', '-created_at'],
                'default_permissions': (),
            },
        ),
    ]
