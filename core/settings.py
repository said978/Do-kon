import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-test-key-saas-pos-change-this-in-production')

DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')

ALLOWED_HOSTS = ['*']
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://192.168.100.213:8000',
    'https://*.onrender.com',
    'https://*.railway.app',
    'https://*.up.railway.app',
]
CUSTOM_CSRF = os.environ.get('CSRF_TRUSTED_ORIGINS')
if CUSTOM_CSRF:
    CSRF_TRUSTED_ORIGINS.extend([origin.strip() for origin in CUSTOM_CSRF.split(',')])
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Uchinchi tomon kutubxonalari
    'rest_framework',
    'corsheaders',
    'drf_spectacular',  # API hujjatlashtirish uchun
    # Bizning ilovalar
    'accounts',
    'inventory',
    'sales',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.TenantMiddleware',
    'accounts.middleware.SubscriptionCheckMiddleware',
    'core.audit_middleware.AuditLogMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.company_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Ma'lumotlar bazasi (PaaS uchun DATABASE_URL, lokal uchun PostgreSQL yoki SQLite)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'saas_pos_db'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'dukon'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
    # Agar PostgreSQL ishlamasa, SQLite ishlatiladi
    import socket
    try:
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = int(os.environ.get('DB_PORT', 5432))
        s = socket.create_connection((db_host, db_port), timeout=2)
        s.close()
    except (ConnectionRefusedError, TimeoutError, OSError):
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]

LANGUAGE_CODE = 'uz'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True

# Statik fayllar (WhiteNoise orqali siqilgan va kesh bilan tarqatiladi)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
SPECTACULAR_SETTINGS = {
    'TITLE': 'DO\'KON POS va Savdo Boshqaruv API',
    'DESCRIPTION': 'Ko\'p filialli va ko\'p foydalanuvchili savdo boshqaruv tizimi API hujjatlari',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),  # Access token 1 kun amal qiladi
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7), # Refresh token 7 kun
    'ROTATE_REFRESH_TOKENS': True,
}
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

JAZZMIN_SETTINGS = {
    "site_title": "DO'KON ERP",
    "site_header": "DO'KON Boshqaruv",
    "site_brand": "DO'KON POS",
    "welcome_sign": "DO'KON Boshqaruv Tizimiga Xush Kelibsiz!",
    "copyright": "DO'KON Retail ERP",
    "search_model": ["inventory.Product", "sales.Customer", "sales.Sale"],

    "topmenu_links": [
        {"name": "Dashboard", "url": "/api/sales/dashboard/", "icon": "fas fa-tachometer-alt"},
        {"name": "Kassa (POS)", "url": "/api/sales/pos/", "icon": "fas fa-cash-register"},
        {"name": "Tovarlar", "url": "/api/inventory/products-page/", "icon": "fas fa-boxes"},
        {"name": "Mijozlar", "url": "/api/sales/customers-page/", "icon": "fas fa-users"},
        {"name": "Hisobotlar", "url": "/api/sales/reports/general/", "icon": "fas fa-chart-line"},
    ],

    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "accounts.Company": "fas fa-building",
        "accounts.Branch": "fas fa-store",
        "accounts.User": "fas fa-user-tie",
        "accounts.AuditLog": "fas fa-shield-alt",
        "inventory.Category": "fas fa-tags",
        "inventory.Product": "fas fa-box",
        "inventory.Stock": "fas fa-warehouse",
        "sales.Customer": "fas fa-users",
        "sales.Sale": "fas fa-receipt",
        "sales.SaleItem": "fas fa-shopping-basket",
        "sales.DebtPayment": "fas fa-hand-holding-usd",
        "sales.SaleReturn": "fas fa-undo-alt",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "show_ui_builder": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "theme": "default",
    "default_theme_mode": "auto",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}