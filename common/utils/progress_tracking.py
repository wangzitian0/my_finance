#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Progress tracking utilities for long-running operations.

Migrated from progress.py with enhanced functionality.

Issue #184: Utility consolidation - Progress tracking
"""

from tqdm import tqdm


def create_progress_bar(total, description="Processing"):
    """
    Return a tqdm progress bar instance.
    """
    return tqdm(total=total, desc=description, unit="ticker")


class ProgressTracker:
    """
    Enhanced progress tracker with multiple progress bars and state management.
    """

    def __init__(self):
        self.progress_bars = {}
        self.states = {}

    def create_progress_bar(self, name: str, total: int, description: str = "Processing"):
        """
        Create a named progress bar.

        Args:
            name: Unique name for the progress bar
            total: Total number of items to process
            description: Description for the progress bar

        Returns:
            tqdm progress bar instance
        """
        if name in self.progress_bars:
            # Close existing progress bar with the same name
            self.progress_bars[name].close()

        progress_bar = tqdm(total=total, desc=description, unit="item")
        self.progress_bars[name] = progress_bar
        self.states[name] = {"current": 0, "total": total}

        return progress_bar

    def update_progress(self, name: str, increment: int = 1):
        """Update progress for a named progress bar."""
        if name in self.progress_bars:
            self.progress_bars[name].update(increment)
            self.states[name]["current"] += increment

    def set_description(self, name: str, description: str):
        """Set description for a named progress bar."""
        if name in self.progress_bars:
            self.progress_bars[name].set_description(description)

    def close_progress_bar(self, name: str):
        """Close a specific progress bar."""
        if name in self.progress_bars:
            self.progress_bars[name].close()
            del self.progress_bars[name]
            del self.states[name]

    def close_all(self):
        """Close all progress bars."""
        for name in list(self.progress_bars.keys()):
            self.close_progress_bar(name)

    def get_progress_state(self, name: str) -> dict:
        """Get current progress state for a named progress bar."""
        return self.states.get(name, {})

    def get_all_states(self) -> dict:
        """Get all progress states."""
        return self.states.copy()


# Global progress tracker instance
_global_progress_tracker = ProgressTracker()


def get_global_progress_tracker() -> ProgressTracker:
    """Get the global progress tracker instance."""
    return _global_progress_tracker
