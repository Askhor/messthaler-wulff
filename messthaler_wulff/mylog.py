import logging

import mydefaults
import tqdm as old_tqdm

DEBUG = -1
INFO = 0
WARNING = 1
ERROR = 2

log = logging.getLogger("messthaler_wulff")
_log_level = 0


def init():
    mydefaults.create_logger("messthaler_wulff")


def get_level() -> int: return _log_level


def set_level(value: int):
    global _log_level
    _log_level = value
    if value <= DEBUG:
        log.setLevel(logging.DEBUG)
    elif value <= INFO:
        log.setLevel(logging.INFO)
    elif value <= WARNING:
        log.setLevel(logging.WARNING)
    else:
        log.setLevel(logging.ERROR)


def tqdm(itr, *args, **kwargs):
    class NoopTqdm:
        def __init__(self, itr):
            self.itr = iter(itr)

        def __next__(self):
            return next(self.itr)

        def __iter__(self):
            return self.itr

        def set_postfix_str(self, *args, **kwargs):
            pass

    if get_level() <= INFO:
        return old_tqdm.tqdm(itr, *args, **kwargs)
    else:
        return NoopTqdm(itr)
