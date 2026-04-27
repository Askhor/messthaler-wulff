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
    """
        Initialize the logger for the 'messthaler_wulff' module.

        This function sets up the logging configurations by calling
        the 'create_logger' method from the 'mydefaults' module.
        """
    mydefaults.create_logger("messthaler_wulff")


def get_level() -> int:
    """
        Retrieve the current logging level.

        Returns:
            int: The current logging level, represented as an integer.
        """
    return _log_level


def set_level(value: int):
    """
        Set the logging level for the logger.

        This function updates the global logging level and configures the
        logger accordingly.

        Args:
            value (int): An integer representing the desired logging level,
                          where lower numbers indicate higher verbosity.
                          Use DEBUG (-1), INFO (0), WARNING (1), ERROR (2).
        """

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
    """
        Wrap an iterable with a progress bar, based on the current logging level.

        If the logging level is set to INFO or lower, a progress bar will be
        displayed using the 'tqdm' library. Otherwise, a no-operation iterator
        will be returned.

        Args:
            itr: The iterable to wrap with a progress bar.
            *args: Additional positional arguments to pass to 'old_tqdm.tqdm'.
            **kwargs: Additional keyword arguments to pass to 'old_tqdm.tqdm'.

        Returns:
            tqdm or NoopTqdm: If the level is set to INFO or lower, returns an
                               instance of 'tqdm'; otherwise, returns an
                               instance of 'NoopTqdm'.
        """

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
