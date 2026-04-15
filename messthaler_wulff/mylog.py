import logging

import tqdm as old_tqdm

DEBUG = -1
INFO = 0
WARNING = 1
ERROR = 2

log = logging.getLogger("messthaler_wulff")
log_level = 0

def tqdm(itr, *args, **kwargs):
    if log_level <= INFO:
        return old_tqdm.tqdm(itr, *args, **kwargs)
    else:
        return itr
