from typing import List


def dictSkipKeys(d: dict | object, keysToSkip: List[str]) -> dict:
    try:
        d = d.__dict__
    except:
        pass
    return {k: v for k, v in d.items() if k not in keysToSkip}


def dictOnlyKeys(d: dict | object, keysToKeep: List[str]) -> dict:
    try:
        d = d.__dict__
    except:
        pass
    return {k: v for k, v in d.items() if k in keysToKeep}
