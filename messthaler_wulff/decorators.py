import logging

log = logging.getLogger("messthaler_wulff")
log.debug(f"Loading {__name__}")


def log_invocation(function):
    def impl(*args, **kwargs):
        parameters = [str(a)[:10] for a in args] + [f"{k}={v}" for k, v in kwargs.items()]
        parameter_string = f"{function.__name__}({", ".join(parameters)})"
        log.debug(f"Calling {parameter_string}")
        result = function(*args, **kwargs)
        log.debug(f"Finished {parameter_string}")
        return result

    return impl
