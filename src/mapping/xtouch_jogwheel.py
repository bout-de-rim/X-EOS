import time
import statistics

class JogWheelHandler:
    def __init__(self):
        self.last_time = time.perf_counter()
        self.time_diffs = []

    def handle(self, value):
        current_time = time.perf_counter()
        time_diff = current_time - self.last_time
        self.last_time = current_time

        self.time_diffs.append(time_diff)
        if len(self.time_diffs) > 4:  # Keep only the last 4 time_diffs
            self.time_diffs.pop(0)

        median_time_diff = statistics.median(self.time_diffs)

        multiplier = self.calculate_multiplier(median_time_diff)

        value = int(value, 16)
        jog_value = (value & 0x3F) * (-1 if (value & 0x40) else 1)
        jog_value *= multiplier

        return jog_value

    def calculate_multiplier(self, time_diff):
        multiplier = max(min(1+ ((1/time_diff)-10)/100, 20), 1)
        print(f"Multiplier: {multiplier}")
        return multiplier
