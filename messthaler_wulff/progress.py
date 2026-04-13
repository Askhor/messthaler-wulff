import time


class BasicProfiler:
    def __init__(self):
        self.datapoints = 0
        self.index = None
        self.last_stop_time = None
        self.last_print_time = time.time()
        self.interval = 1
        self.sums = []

    def maybe_print(self):
        t = time.time()
        if t >= self.last_print_time + self.interval:
            self.last_print_time = t

            print("===== Profiling Result =====")
            for i, s in enumerate(self.sums):
                print(f"{i:2} {s // self.datapoints:10,}")

    def new_run(self):
        self.datapoints += 1
        self.index = 0
        self.last_stop_time = time.time_ns()

        self.maybe_print()

        self.add_stop()

    def add_stop(self):
        now = time.time_ns()

        while self.index >= len(self.sums):
            self.sums.append(0)
        self.sums[self.index] += now - self.last_stop_time
        self.index += 1


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
