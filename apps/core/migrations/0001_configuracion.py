from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Configuracion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_empresa', models.CharField(default='Gibit Tecnología', max_length=200, verbose_name='Nombre empresa')),
                ('ruc', models.CharField(blank=True, max_length=11, verbose_name='RUC')),
                ('direccion', models.CharField(blank=True, max_length=300, verbose_name='Dirección')),
                ('telefono', models.CharField(blank=True, max_length=50, verbose_name='Teléfono')),
                ('email', models.EmailField(blank=True, verbose_name='Email')),
                ('web', models.CharField(blank=True, max_length=100, verbose_name='Sitio web')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='config/', verbose_name='Logo')),
                ('slogan', models.CharField(blank=True, max_length=150, verbose_name='Slogan / Descripción')),
            ],
            options={
                'verbose_name': 'Configuración',
                'verbose_name_plural': 'Configuración',
            },
        ),
    ]
