"""
background/idle_monitor.py

Handles idle time and overnight period detection for GAIA background processing.
"""

import time
import datetime
import logging

logger = logging.getLogger("GAIA")

class IdleMonitor:
    def __init__(self, config):
        """
        Initialize the Idle Monitor.

        Args:
            config: Configuration object with idle settings.
        """
        self.config = config
        self.last_activity_time = time.time()

    def register_activity(self) -> None:
        """
        Register user activity to reset the idle timer.
        """
        self.last_activity_time = time.time()

    def is_idle(self) -> bool:
        """
        Check if the system has been idle longer than the configured threshold.

        Returns:
            True if idle, False otherwise.
        """
        idle_threshold = getattr(self.config, 'idle_threshold', 300)  # Default 5 minutes
        idle_duration = time.time() - self.last_activity_time
        logger.debug(f"Idle time check: {idle_duration:.2f}s (threshold: {idle_threshold}s)")
        return idle_duration > idle_threshold

    def is_long_idle(self) -> bool:
        """
        Check if the system has been idle longer than the long idle threshold.

        Returns:
            True if long idle, False otherwise.
        """
        long_idle_threshold = getattr(self.config, 'long_idle_threshold', 1800)  # Default 30 minutes
        idle_duration = time.time() - self.last_activity_time
        logger.debug(f"Long idle time check: {idle_duration:.2f}s (threshold: {long_idle_threshold}s)")
        return idle_duration > long_idle_threshold

    def is_overnight_period(self) -> bool:
        """
        Check if the current time falls within the overnight processing window.

        Returns:
            True if within overnight hours, False otherwise.
        """
        if not getattr(self.config, 'overnight_processing', False):
            return False

        current_hour = datetime.datetime.now().hour
        start_hour = getattr(self.config, 'overnight_start_hour', 22)
        end_hour = getattr(self.config, 'overnight_end_hour', 6)

        if start_hour > end_hour:
            # Overnight window crosses midnight
            in_window = current_hour >= start_hour or current_hour < end_hour
        else:
            in_window = start_hour <= current_hour < end_hour

        logger.debug(f"Overnight period check: {'YES' if in_window else 'NO'} (Current hour: {current_hour})")
        return in_window