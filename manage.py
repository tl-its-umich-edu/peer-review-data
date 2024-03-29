# -*- coding: utf-8 -*-
import logging
import os
import sys

from dotenv import load_dotenv

CONFIG_DIR: str = os.getenv('ENV_DIR', os.path.join('config', 'secrets'))
ENV_PATH = os.path.join(CONFIG_DIR, os.getenv('ENV_FILE', '.env'))
load_dotenv(dotenv_path=ENV_PATH, verbose=True)

LOGGER = logging.getLogger(__name__)

if '__main__' == __name__:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                          'peer_review_data.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        LOGGER.error('django.core.management not found')
    execute_from_command_line(sys.argv)
