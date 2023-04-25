# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from peer_review_data.main import main


class Command(BaseCommand):
    """
    Django management command used to run the process defined
    in the main module.
    """

    def handle(self, *args, **options) -> None:
        main()
