import time


def debounce(interval=1):
    def deco(function):
        last_call = [None]

        def impl(*args, **kwargs):
            if last_call[0] is None:
                last_call[0] = time.time()
                return

            t = time.time()
            if t >= last_call[0] + interval:
                last_call[0] = t
                function(*args, **kwargs)

        return impl

    return deco
