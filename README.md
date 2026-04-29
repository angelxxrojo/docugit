# DocuGit - Sistema de Gestion Empresarial

Sistema integral de gestion para empresas de servicios tecnologicos. Desarrollado con Django, cubre el ciclo completo desde la captacion de clientes hasta la ejecucion y cierre de proyectos.

**Stack:** Django 6.0.4 | SQLite | Tailwind CSS | Alpine.js | HTMX

---

## Requisitos previos

- Python 3.11+
- pip

## Instalacion

```bash
# 1. Clonar el repositorio
git clone <URL_DEL_REPOSITORIO>
cd docugit

# 2. Crear entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar migraciones
python manage.py migrate

# 5. Cargar datos geograficos (UBIGEO Peru)
python manage.py loaddata apps/location/fixtures/countries.json
python manage.py loaddata apps/location/fixtures/departments.json
python manage.py loaddata apps/location/fixtures/provinces.json
python manage.py loaddata apps/location/fixtures/districts.json

# 6. Crear superusuario
python manage.py createsuperuser

# 7. Levantar el servidor
python manage.py runserver
```

Acceder a `http://127.0.0.1:8000/`

## Estructura del proyecto

```
docugit/
├── config/
│   ├── settings/
│   │   ├── base.py          # Configuracion base
│   │   ├── development.py   # Overrides desarrollo
│   │   └── production.py    # Overrides produccion
│   ├── urls.py               # Rutas principales
│   └── wsgi.py
├── apps/
│   ├── core/                 # Modelos base y configuracion del sistema
│   ├── usuarios/             # Autenticacion y roles
│   ├── clientes/             # CRM (empresas, contactos, sedes)
│   ├── catalogo/             # Servicios, productos, condiciones, cuentas bancarias
│   ├── proformas/            # Cotizaciones con versionado
│   ├── proyectos/            # Gestion de proyectos y Kanban
│   ├── documentos/           # Plantillas y repositorio de archivos
│   ├── location/             # Datos geograficos UBIGEO Peru
│   └── templates/            # Templates HTML
├── static/                   # CSS, JS, plugins
├── media/                    # Archivos subidos
├── requirements.txt
└── manage.py
```

## Variables de entorno

| Variable | Descripcion | Default |
|----------|-------------|---------|
| `DJANGO_SETTINGS_MODULE` | Modulo de configuracion | `config.settings.development` |
| `SECRET_KEY` | Clave secreta Django | (generada en settings) |
| `DEBUG` | Modo debug | `True` (development) |

## Dependencias

| Paquete | Version | Uso |
|---------|---------|-----|
| Django | 6.0.4 | Framework web |
| django-htmx | 1.27.0 | Integracion HTMX para interacciones AJAX |
| django-widget-tweaks | 1.5.1 | Personalizacion de widgets en formularios |
| whitenoise | 6.12.0 | Servicio de archivos estaticos |

## Notas

- La base de datos es SQLite (`gibit.sqlite3`) para desarrollo. Para produccion se recomienda PostgreSQL.
- Los archivos estaticos del frontend (Tailwind CSS, Alpine.js, HTMX) se sirven via CDN o archivos locales en `/static/js/plugins/`.
- El sistema usa localizacion `es-pe` con zona horaria `America/Lima`.
