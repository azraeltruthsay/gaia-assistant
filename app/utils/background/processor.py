"""
background/processor.py

BackgroundProcessor handles idle-time and overnight-time task processing.
"""

import time
import datetime
import logging
import threading
from .task_queue import TaskQueue
from .idle_monitor import IdleMonitor
from .background_tasks import BackgroundTasks

logger = logging.getLogger("GAIA")

class BackgroundProcessor:
    def __init__(self, config, ai_manager=None):
        self.config = config
        self.ai_manager = ai_manager
        self.task_queue = TaskQueue(status_file=config.task_status_path)
        self.idle_monitor = IdleMonitor(config)
        self.task_handler = BackgroundTasks(ai_manager)
        self.is_running = False

    def start(self):
        if not self.is_running:
            self.is_running = True
            logger.info("🚀 BackgroundProcessor started")
            thread = threading.Thread(target=self._worker_loop, daemon=True)
            thread.start()

    def stop(self):
        self.is_running = False
        logger.info("🛑 BackgroundProcessor stopped")

    def register_activity(self):
        self.idle_monitor.register_activity()
        logger.debug("🔄 User activity registered, idle timer reset")

    def _worker_loop(self):
        logger.info("🌀 Entering BackgroundProcessor worker loop")
        while self.is_running:
            try:
                should_process = self.idle_monitor.is_idle() or self.idle_monitor.is_overnight_period()
                long_idle = self.idle_monitor.is_long_idle()

                if not should_process:
                    logger.debug("💤 System not idle or overnight, sleeping for 60s")
                    time.sleep(60)
                    continue

                next_task_info = self.task_queue.get_next_task(long_idle=long_idle)
                if not next_task_info:
                    logger.debug("📭 No pending tasks found, sleeping for 60s")
                    time.sleep(60)
                    continue

                priority, task = next_task_info
                logger.info(f"📌 Processing task {task['id']} of type '{task['type']}' (attempt {task['attempts'] + 1})")

                result = self._process_task(task)

                if result.get("success"):
                    logger.info(f"✅ Task {task['id']} completed successfully")
                    self.task_queue.task_status["pending_tasks"] = [t for t in self.task_queue.task_status["pending_tasks"] if t["id"] != task["id"]]
                    self.task_queue.task_status["completed_tasks"].append(task)
                else:
                    task["error"] = result.get("error", "Unknown error")
                    max_retries = getattr(self.config, 'max_retries', 3)
                    if task["attempts"] >= max_retries:
                        logger.warning(f"❌ Task {task['id']} failed after {task['attempts']} attempts")
                        self.task_queue.task_status["pending_tasks"] = [t for t in self.task_queue.task_status["pending_tasks"] if t["id"] != task["id"]]
                        self.task_queue.task_status["failed_tasks"].append(task)
                    else:
                        logger.info(f"🔁 Requeuing task {task['id']} (attempt {task['attempts']})")
                        self.task_queue.requeue_task_with_backoff(task, priority, task["attempts"])

                self.task_queue.save_status()
                logger.debug("⏳ Task queue status saved, sleeping 5s before next loop")
                time.sleep(5)

            except Exception as e:
                logger.error(f"🔥 Worker loop error: {e}", exc_info=True)
                time.sleep(60)

    def _process_task(self, task):
        task["attempts"] += 1
        task["last_attempt"] = datetime.datetime.now().isoformat()

        try:
            if task["type"] == "summarize_conversation":
                return self.task_handler.process_conversation_task(task)
            elif task["type"] == "embed_document":
                return self.task_handler.process_embedding_task(task)
            elif task["type"] == "lora_training":
                return self.task_handler.process_lora_task(task, self.config)
            else:
                logger.warning(f"⚠️ Unknown task type: {task['type']}")
                return {"success": False, "error": "Unknown task type"}
        except Exception as e:
            logger.error(f"❌ Exception while processing task {task['id']}: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def get_task_status(self):
        """Return live status of task queue."""
        try:
            return {
                "status": "running" if self.is_running else "stopped",
                "pending": len(self.task_queue.task_status.get("pending_tasks", [])),
                "completed": len(self.task_queue.task_status.get("completed_tasks", [])),
                "failed": len(self.task_queue.task_status.get("failed_tasks", [])),
                "active_task_queue": self.task_queue.task_status
            }
        except Exception as e:
            logger.error(f"Error retrieving background task status: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e)
            }
