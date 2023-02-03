# -*- coding: utf-8 -*-
from typing import List


def dictSkipKeys(d: dict | object, keysToSkip: List[str]) -> dict:
    '''
    Return a dictionary from a `dict` or `object` without the keys
    specified.  Keys that aren't present in `d` are silently skipped.

    :param d: A `dict` or `object` with some keys to skip, others to keep.
    :param keysToKeep: A `List` of `str` key names to be skipped.
    :return: A `dict` without the specified keys.
    '''
    try:
        d = d.__dict__
    except:
        pass
    return {k: v for k, v in d.items() if k not in keysToSkip}


def dictKeepKeys(d: dict | object, keysToKeep: List[str]) -> dict:
    '''
    Return a dictionary from a `dict` or `object` containing only the keys
    specified.  Keys that aren't present in `d` are silently skipped.

    :param d: A `dict` or `object` with some keys to keep, others to skip.
    :param keysToKeep: A `List` of `str` key names to be kept.
    :return: A `dict` with only the specified keys.
    '''
    try:
        d = d.__dict__
    except:
        pass
    return {k: v for k, v in d.items() if k in keysToKeep}
