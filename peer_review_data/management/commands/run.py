# standard libraries
import logging, os, sys
from logging import Logger

# third-party libraries
from django.core.management.base import BaseCommand

# local libraries
from constants import API_CONFIG_PATH
from peer-review-data.main import main


LOGGER: Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django management command used for launching the process defined in the main module.
    """

    def handle(self, *args, **options) -> None:
        main()
