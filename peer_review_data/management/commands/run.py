# -*- coding: utf-8 -*-
from logging import Logger, getLogger

from django.core.management.base import BaseCommand

from peer_review_data.main import main

LOGGER: Logger = getLogger(__name__)


class Command(BaseCommand):
    """
    Django management command used for launching the process defined
    in the main module.
    """

    def handle(self, *args, **options) -> None:
        """
        Entrypoint method required by BaseCommand class (see Django docs).
        """
        main()
