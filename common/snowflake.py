# common/snowflake.py
import threading
import time


class Snowflake:
    """
    A simple Snowflake ID generator.
    Generates 64-bit IDs based on the current timestamp, a machine ID, and a sequence number.
    """

    def __init__(self, machine_id=1):
        self.machine_id = machine_id & 0x3FF  # 10 bits for machine id
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()

    def _timestamp(self):
        return int(time.time() * 1000)

    def get_id(self):
        with self.lock:
            timestamp = self._timestamp()
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & 0xFFF  # 12-bit sequence
                if self.sequence == 0:
                    # wait until next millisecond
                    while timestamp <= self.last_timestamp:
                        timestamp = self._timestamp()
            else:
                self.sequence = 0
            self.last_timestamp = timestamp
            # Construct ID: 41 bits timestamp, 10 bits machine id, 12 bits sequence
            return (timestamp << 22) | (self.machine_id << 12) | self.sequence
