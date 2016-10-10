# -*- coding: utf-8 -*-
import re
import logging

logger = logging.getLogger('caffeine.models')


def slugify(string):
    return re.sub(r'\W+', '', string).lower()
