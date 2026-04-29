import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0003_add_moneda_redesign_tipocambio'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoriaProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nombre', models.CharField(max_length=100, unique=True, verbose_name='Nombre')),
                ('descripcion', models.CharField(blank=True, max_length=255, verbose_name='Descripción')),
                ('activo', models.BooleanField(default=True, verbose_name='Activa')),
            ],
            options={
                'verbose_name': 'Categoría de producto',
                'verbose_name_plural': 'Categorías de producto',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nombre', models.CharField(max_length=200, verbose_name='Nombre')),
                ('marca', models.CharField(blank=True, max_length=100, verbose_name='Marca')),
                ('modelo', models.CharField(
                    blank=True, db_index=True, max_length=150, verbose_name='Modelo',
                    help_text='Código de modelo del fabricante. Facilita búsqueda e importación.',
                )),
                ('descripcion', models.TextField(blank=True, verbose_name='Especificaciones técnicas')),
                ('unidad', models.CharField(
                    choices=[
                        ('unidad', 'Unidad'), ('par', 'Par'), ('rollo', 'Rollo'),
                        ('metro', 'Metro'), ('kit', 'Kit'), ('caja', 'Caja'),
                        ('licencia', 'Licencia'), ('global', 'Global'),
                    ],
                    default='unidad', max_length=20, verbose_name='Unidad',
                )),
                ('precio_usd', models.DecimalField(
                    decimal_places=2, default=0, max_digits=10, verbose_name='Precio (USD)',
                )),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('categoria', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='productos',
                    to='catalogo.categoriaproducto',
                    verbose_name='Categoría',
                )),
            ],
            options={
                'verbose_name': 'Producto',
                'verbose_name_plural': 'Productos',
                'ordering': ['categoria__nombre', 'nombre'],
            },
        ),
    ]
