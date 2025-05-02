"""
ethics/ethical_sentinel.py

The Ethical Sentinel monitors system health and cognitive strain for GAIA.
"""

import time
import psutil  # lightweight system monitor

class EthicalSentinel:
    def __init__(self, ai_manager=None, cpu_threshold=85, memory_threshold=85, loop_threshold=5, error_threshold=10):
        """
        Initialize the Ethical Sentinel.

        Args:
            ai_manager: Optional AI manager reference.
            cpu_threshold: % CPU usage considered critical.
            memory_threshold: % memory usage considered critical.
            loop_threshold: Max retries before considering an operation stuck.
            error_threshold: Max unhandled errors before alerting.
        """
        self.ai_manager = ai_manager
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.loop_threshold = loop_threshold
        self.error_threshold = error_threshold
        self.loop_counts = {}
        self.error_counts = 0

    def monitor_resources(self):
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent

        if cpu > self.cpu_threshold:
            self.alert(f"High CPU usage detected: {cpu}%")
        
        if memory > self.memory_threshold:
            self.alert(f"High memory usage detected: {memory}%")

    def monitor_loops(self, loop_id):
        """
        Track loops or task retries.
        """
        if loop_id not in self.loop_counts:
            self.loop_counts[loop_id] = 0
        self.loop_counts[loop_id] += 1

        if self.loop_counts[loop_id] > self.loop_threshold:
            self.alert(f"Possible infinite loop or cognitive jam detected at {loop_id}")

    def monitor_errors(self):
        self.error_counts += 1
        if self.error_counts > self.error_threshold:
            self.alert(f"High error rate detected: {self.error_counts} unhandled errors")

    def reset_loop(self, loop_id):
        if loop_id in self.loop_counts:
            del self.loop_counts[loop_id]

    def reset_errors(self):
        self.error_counts = 0

    def alert(self, message):
        print(f"[🛡️ Ethical Sentinel Alert] {message}")
        if self.ai_manager:
            self.ai_manager.handle_ethical_alert(message)
