import os
from pathlib import Path

# BASE_DIR ni standart usulda belgilash (agar run_app dan import ishlamasa)
BASE_DIR = Path(__file__).resolve().parent.parent

LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
ALLOWED_HOSTS = ['*']

USE_I18N = True
USE_TZ = True
AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    # ... sizdagi boshqa middleware'lar ...
    'accounts.middleware.SubscriptionCheckMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'CONN_MAX_AGE': 0,
        'OPTIONS': {
            'DISABLE_SERVER_SIDE_CURSORS': True,
        }
    }
}

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # <--- Shu qatorda BASE_DIR / 'templates' bo'lishi shart
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
# Django admin panelida bir vaqtning o'zida ko'p obyektlar bilan ishlash uchun cheklovni oshirish
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000  # Standart 1000 o'rniga 10000 ga oshiriladi