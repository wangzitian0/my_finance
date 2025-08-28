#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ID generation utilities including Snowflake ID system.

Migrated from snowflake.py with enhanced functionality.

Issue #184: Utility consolidation - ID generation
"""

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

            # Generate the final ID
            # 41 bits for timestamp + 10 bits for machine ID + 12 bits for sequence
            snowflake_id = (timestamp << 22) | (self.machine_id << 12) | self.sequence
            return snowflake_id

    def get_str_id(self):
        """Get string representation of Snowflake ID"""
        return str(self.get_id())


# Global Snowflake instance for convenience
_default_snowflake = Snowflake()


def generate_snowflake_id() -> int:
    """Generate a Snowflake ID using the default instance"""
    return _default_snowflake.get_id()


def generate_snowflake_str() -> str:
    """Generate a Snowflake ID string using the default instance"""
    return _default_snowflake.get_str_id()