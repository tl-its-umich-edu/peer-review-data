# -*- coding: utf-8 -*-
import os
import sys
from logging import Logger, getLogger
from typing import List

LOGGER: Logger = getLogger(__name__)

CANVAS_BASE_URL: str = os.getenv('CANVAS_BASE_URL')
CANVAS_API_TOKEN: str = os.getenv('CANVAS_API_TOKEN')
COURSE_IDS_CSV: str = os.getenv('COURSE_IDS_CSV')
COURSE_IDS: List[str] = [
    c.strip() for c in COURSE_IDS_CSV.split(',') if c
] if COURSE_IDS_CSV else None


def checkConfig():
    envErrors = []

    if CANVAS_BASE_URL is None:
        envErrors.append('CANVAS_BASE_URL')

    if CANVAS_API_TOKEN is None:
        envErrors.append('CANVAS_API_TOKEN')

    if COURSE_IDS_CSV is None:
        envErrors.append('COURSE_IDS_CSV')

    if len(envErrors) > 0:
        LOGGER.critical('The following environment variable(s) are not set: '
                        f'{", ".join(envErrors)}')
        sys.exit()

    if COURSE_IDS is None:
        LOGGER.critical('COURSE_IDS could not be set. '
                        '(Problem parsing COURSE_IDS_CSV?)')
        sys.exit()


checkConfig()
