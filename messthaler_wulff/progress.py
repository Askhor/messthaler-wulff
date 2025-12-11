import os
import time

import psutil


class ProgressBar:
    def __init__(self, goal=None, energy_callback=None):
        self.last_measurement = time.time()
        self.measurements = []
        self.interval = 1
        self.memory = 10
        self.goal = goal
        self.initial_memory_usage = ProgressBar.process_memory()
        self.energy_callback = energy_callback

    def __call__(self, value):
        t = time.time()
        if t >= self.last_measurement + self.interval:
            self.measurements.append((t, value))
            self.last_measurement = t

            print(self)

    def rate(self):
        while True:
            if len(self.measurements) < 2:
                return 0

            t1, m1 = self.measurements[0]
            t2, m2 = self.measurements[-1]

            if t2 - t1 > self.memory:
                self.measurements.pop(0)
                continue

            return (m2 - m1) / (t2 - t1)

    @staticmethod
    def process_memory():
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        return mem_info.rss

    @staticmethod
    def format_mem(m):
        exponent = 0
        while m >= 1000 and exponent < 3:
            m /= 1000
            exponent += 1

        postfix = ["B", "KB", "MB", "GB"][exponent]

        return f"{m:.1f} {postfix}"

    @staticmethod
    def format_time(s):
        out = []
        hours = s // 3600
        s -= hours * 3600
        if hours > 0:
            out.append(f"{hours:.0f}h")

        minutes = s // 60
        s -= minutes * 60

        if minutes > 0:
            out.append(f"{minutes:.0f}m")

        if s > 0:
            out.append(f"{s:.0f}s")

        return " ".join(out)

    def __str__(self):
        r = self.rate()
        out = f"{r:10.2f}/s"

        current_value = None

        if self.goal is not None:
            current_value = self.measurements[-1][1]
            out += f" {current_value}/{self.goal}"

        if self.goal is not None and r != 0:
            t = (self.goal - current_value) / r
            out += f" {self.format_time(t)}"

        out += f" {ProgressBar.format_mem(ProgressBar.process_memory() - self.initial_memory_usage)}"

        if self.energy_callback is not None:
            out += " " + str(self.energy_callback()) + " energy"

        return out


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
