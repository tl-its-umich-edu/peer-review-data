from typing import List


def dictSkipKeys(d: dict, keysToSkip: List[str]) -> dict:
    return {k: v for k, v in d.items() if k not in keysToSkip}

def dictOnlyKeys(d: dict, keysToKeep: List[str]) -> dict:
    return {k: v for k, v in d.items() if k in keysToKeep}
