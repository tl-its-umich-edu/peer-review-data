# -*- coding: utf-8 -*-
import os
from typing import Any

# Django settings

BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))

CONFIG_DIR: str = os.path.join(
    BASE_DIR, os.getenv('ENV_DIR', os.path.join('config', 'secrets')))

DATABASES: dict[str, dict[str, Any]] = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'peer-review-data'),
        'USER': os.getenv('DB_USER', 'peer-review-data'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'peer-review-data_pw'),
        'HOST': os.getenv('DB_HOST', 'peer-review-data_db'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {'charset': 'utf8mb4'},
        'TEST': {
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_ci'
        }
    }
}

DATETIME_FORMAT: str = "N j, Y g:i:s a"

if bool(int(os.getenv('EMAIL_DEBUG', '1'))):
    EMAIL_BACKEND: str = 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST: str = os.getenv('SMTP_HOST', '')
EMAIL_PORT: int = int(os.getenv('SMTP_PORT', 0))
EMAIL_USE_TLS: bool = True

LOGGING: dict[str, Any] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s:%(lineno)d - %(funcName)s '
                      '- %(levelname)s - %(message)s '
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        }
    },
    'root': {
        'handlers': ['console'],
        'level': os.getenv('LOG_LEVEL', 'INFO').upper()
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('LOG_LEVEL', 'INFO').upper(),
            'propagate': False
        }
    }
}

INSTALLED_APPS: list[str] = [
    'peer_review_data'
]

SECRET_KEY: str = os.getenv('SECRET_KEY', '-- A SECRET KEY --')

TIME_ZONE: str = os.getenv('TIME_ZONE', 'UTC')
USE_TZ: bool = True
