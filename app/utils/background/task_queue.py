"""
background/task_queue.py

Handles task queue management for GAIA background processing.
Manages adding tasks, saving/loading task status, and retry logic.
"""

import os
import json
import queue
import threading
import datetime
import logging
from typing import Dict, Any

logger = logging.getLogger("GAIA")

class TaskQueue:
    def __init__(self, status_file: str):
        """
        Initialize the Task Queue Manager.

        Args:
            status_file: Path to the task status JSON file.
        """
        self.status_file = status_file
        self.task_queue = queue.PriorityQueue()
        self.task_lock = threading.Lock()
        self.status_lock = threading.Lock()
        self.task_status = {
            "completed_tasks": [],
            "pending_tasks": [],
            "failed_tasks": []
        }
        self.load_status()

    def load_status(self) -> None:
        """
        Load task status from the status file.
        """
        try:
            with self.status_lock:
                if os.path.exists(self.status_file):
                    with open(self.status_file, 'r', encoding='utf-8') as f:
                        self.task_status = json.load(f)
        except Exception as e:
            logger.error(f"Error loading task status: {e}")

    def save_status(self) -> None:
        """
        Save current task status to the status file.
        """
        try:
            with self.status_lock:
                with open(self.status_file, 'w', encoding='utf-8') as f:
                    json.dump(self.task_status, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving task status: {e}")

    def add_task(self, task_type: str, priority: int, data: Dict[str, Any]) -> str:
        """
        Add a task to the task queue.

        Args:
            task_type: Type of the task (e.g., 'summarize_conversation')
            priority: Priority of the task (lower number = higher priority)
            data: Task-specific data dictionary

        Returns:
            Task ID string
        """
        task_id = f"{task_type}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        task = {
            "id": task_id,
            "type": task_type,
            "status": "pending",
            "created": datetime.datetime.now().isoformat(),
            "data": data,
            "attempts": 0,
            "last_attempt": None,
            "result": None
        }

        with self.task_lock:
            self.task_queue.put((priority, task))

        with self.status_lock:
            self.task_status["pending_tasks"].append(task)
            self.save_status()

        logger.info(f"Added task: {task_id} (Type: {task_type}, Priority: {priority})")
        return task_id

    def get_next_task(self, long_idle: bool) -> Any:
        """
        Get the next task to process based on idle time.

        Args:
            long_idle: Whether the system has been idle for a long time

        Returns:
            Tuple of (priority, task) or None if no task is ready
        """
        with self.task_lock:
            try:
                if long_idle:
                    return self.task_queue.get(block=False)
                else:
                    # Prioritize only high-priority tasks (<= 20)
                    all_tasks = []
                    while not self.task_queue.empty():
                        p, t = self.task_queue.get(block=False)
                        all_tasks.append((p, t))
                    for p, t in all_tasks:
                        if p <= 20:
                            # Put the others back
                            for item in all_tasks:
                                if item != (p, t):
                                    self.task_queue.put(item)
                            return p, t
                    # No high-priority tasks found
                    for item in all_tasks:
                        self.task_queue.put(item)
            except queue.Empty:
                return None

    def requeue_task_with_backoff(self, task: Dict[str, Any], original_priority: int, attempts: int, retry_base: int = 2) -> None:
        """
        Requeue a failed task with backoff priority.

        Args:
            task: The failed task dictionary
            original_priority: Original task priority
            attempts: Number of previous attempts
            retry_base: Base factor for backoff calculation
        """
        new_priority = original_priority + (retry_base ** (attempts - 1)) * 5
        with self.task_lock:
            self.task_queue.put((new_priority, task))
        logger.warning(f"Task {task['id']} re-queued with new priority {new_priority}")
