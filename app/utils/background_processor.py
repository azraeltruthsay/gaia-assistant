"""
Background processing module for GAIA D&D Campaign Assistant.
Handles idle-time tasks like conversation summarization and LoRA fine-tuning.
"""

import os
import time
import threading
import logging
import queue
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# Get the logger
logger = logging.getLogger("GAIA")

class BackgroundProcessor:
    """Manages background processing tasks during system idle time."""
    
    def __init__(self, config, ai_manager=None):
        """
        Initialize the Background Processor.
        
        Args:
            config: Configuration object
            ai_manager: AI Manager for LLM access
        """
        self.config = config
        self.ai_manager = ai_manager
        self.task_queue = queue.PriorityQueue()
        self.is_running = False
        self.worker_thread = None
        self.idle_threshold = 300  # 5 minutes of inactivity before starting tasks
        self.last_activity_time = time.time()
        self.current_task = None
        
        # Add locks for thread safety
        self.task_lock = threading.Lock()
        self.status_lock = threading.Lock()
        
        # Set up directories
        self.raw_archives_dir = os.path.join(
            config.data_path, "../conversation_archives"
        )
        self.structured_archives_dir = os.path.join(
            config.data_path, "../structured_archives"
        )
        
        # Create directories if they don't exist
        os.makedirs(self.raw_archives_dir, exist_ok=True)
        os.makedirs(self.structured_archives_dir, exist_ok=True)
        
        # Status file for tracking progress
        self.status_file = os.path.join(config.data_path, "../background_tasks.json")
        self.load_status()
        
        logger.info("Background Processor initialized")
    
    def start(self):
        """Start the background processing thread."""
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            logger.info("Background processing started")
            return True
        return False
    
    def stop(self):
        """Stop the background processing thread."""
        if self.is_running:
            self.is_running = False
            if self.worker_thread:
                self.worker_thread.join(timeout=2.0)
            logger.info("Background processing stopped")
            return True
        return False
    
    def load_status(self):
        """Load task status from status file."""
        try:
            with self.status_lock:
                if os.path.exists(self.status_file):
                    with open(self.status_file, 'r', encoding='utf-8') as f:
                        self.task_status = json.load(f)
                else:
                    self.task_status = {
                        "completed_tasks": [],
                        "pending_tasks": [],
                        "failed_tasks": []
                    }
        except Exception as e:
            logger.error(f"Error loading task status: {e}")
            self.task_status = {
                "completed_tasks": [],
                "pending_tasks": [],
                "failed_tasks": []
            }
    
    def save_status(self):
        """Save current task status to status file."""
        try:
            with self.status_lock:
                with open(self.status_file, 'w', encoding='utf-8') as f:
                    json.dump(self.task_status, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving task status: {e}")
    
    def register_activity(self):
        """Register user activity to prevent processing during active use."""
        self.last_activity_time = time.time()
    
    def is_idle(self):
        """Check if the system has been idle for the threshold period."""
        return (time.time() - self.last_activity_time) > self.idle_threshold
    
    def add_task(self, task_type, priority, data):
        """
        Add a task to the processing queue.
        
        Args:
            task_type: Type of task (e.g., 'summarize_conversation', 'embed_document')
            priority: Priority level (lower number = higher priority)
            data: Task-specific data
            
        Returns:
            Task ID
        """
        task_id = f"{task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        task = {
            "id": task_id,
            "type": task_type,
            "status": "pending",
            "created": datetime.now().isoformat(),
            "data": data,
            "attempts": 0,
            "last_attempt": None,
            "result": None
        }
        
        # Thread-safe update of task queue and status
        with self.task_lock:
            # Add to queue 
            self.task_queue.put((priority, task))
        
        # Thread-safe update of task status
        with self.status_lock:
            # Update status file
            self.task_status["pending_tasks"].append(task)
            self.save_status()
        
        logger.info(f"Added task: {task_id} (Type: {task_type}, Priority: {priority})")
        return task_id
    
    def add_conversation_processing_task(self, archive_id, raw_content):
        """
        Add a conversation processing task.
        
        Args:
            archive_id: ID of the archived conversation
            raw_content: Raw conversation content or path to file
            
        Returns:
            Task ID
        """
        # Save raw content to file if it's not a path
        raw_path = raw_content if isinstance(raw_content, str) and os.path.exists(raw_content) else None
        
        if not raw_path:
            raw_path = os.path.join(self.raw_archives_dir, f"{archive_id}.md")
            if not os.path.exists(raw_path):
                try:
                    with open(raw_path, 'w', encoding='utf-8') as f:
                        f.write(raw_content)
                except Exception as e:
                    logger.error(f"Error saving raw conversation: {e}")
                    return None
        
        # Add processing task - priority 10 (medium)
        return self.add_task(
            "summarize_conversation", 
            10, 
            {
                "archive_id": archive_id,
                "raw_path": raw_path,
                "output_path": os.path.join(self.structured_archives_dir, f"{archive_id}_structured.md")
            }
        )
    
    def add_embedding_task(self, file_path):
        """
        Add a document embedding task.
        
        Args:
            file_path: Path to the document to embed
            
        Returns:
            Task ID
        """
        # Add embedding task - priority 20 (lower than summarization)
        return self.add_task(
            "embed_document", 
            20, 
            {"file_path": file_path}
        )
    
    def add_lora_training_task(self, file_paths):
        """
        Add a LoRA fine-tuning task.
        
        Args:
            file_paths: List of file paths to use for fine-tuning
            
        Returns:
            Task ID
        """
        # Add LoRA training task - priority 30 (lowest)
        return self.add_task(
            "lora_training", 
            30, 
            {"file_paths": file_paths}
        )
    
    def _worker_loop(self):
        """Main worker loop for processing background tasks."""
        logger.info("Background processor worker loop started")
        
        while self.is_running:
            try:
                # Check if system is idle
                if not self.is_idle():
                    time.sleep(60)  # Check again in a minute
                    continue
                
                # Check if queue is empty
                if self.task_queue.empty():
                    time.sleep(60)  # Check again in a minute
                    continue
                
                # Thread-safe retrieval of a task
                with self.task_lock:
                    # Get the highest priority task
                    try:
                        priority, task = self.task_queue.get(block=False)
                    except queue.Empty:
                        # Double-check in case another thread took the last task
                        continue
                
                # Set as current task
                with self.status_lock:
                    self.current_task = task
                    
                    # Update task status
                    task["status"] = "processing"
                    task["attempts"] += 1
                    task["last_attempt"] = datetime.now().isoformat()
                    
                    # Update task in pending tasks
                    for i, pending_task in enumerate(self.task_status["pending_tasks"]):
                        if pending_task["id"] == task["id"]:
                            self.task_status["pending_tasks"][i] = task
                            break
                    
                    self.save_status()
                
                logger.info(f"Processing task: {task['id']} (Type: {task['type']})")
                
                # Process task based on type
                if task["type"] == "summarize_conversation":
                    result = self._process_conversation_task(task)
                elif task["type"] == "embed_document":
                    result = self._process_embedding_task(task)
                elif task["type"] == "lora_training":
                    result = self._process_lora_task(task)
                else:
                    logger.warning(f"Unknown task type: {task['type']}")
                    result = {"success": False, "error": "Unknown task type"}
                
                # Thread-safe update of task status
                with self.status_lock:
                    # Update task status
                    if result["success"]:
                        task["status"] = "completed"
                        task["result"] = result
                        
                        # Move from pending to completed
                        self.task_status["pending_tasks"] = [t for t in self.task_status["pending_tasks"] if t["id"] != task["id"]]
                        self.task_status["completed_tasks"].append(task)
                        
                        # Apply size limits to completed tasks list
                        if len(self.task_status["completed_tasks"]) > 100:
                            self.task_status["completed_tasks"] = self.task_status["completed_tasks"][-100:]
                        
                        # If this was a summarization task, add an embedding task
                        if task["type"] == "summarize_conversation" and "output_path" in result:
                            # Release the lock before adding a new task to avoid deadlock
                            with self.task_lock:
                                self.add_embedding_task(result["output_path"])
                        
                        logger.info(f"Task completed: {task['id']}")
                    else:
                        if task["attempts"] >= 3:
                            task["status"] = "failed"
                            task["result"] = result
                            
                            # Move from pending to failed
                            self.task_status["pending_tasks"] = [t for t in self.task_status["pending_tasks"] if t["id"] != task["id"]]
                            self.task_status["failed_tasks"].append(task)
                            
                            # Apply size limits to failed tasks list
                            if len(self.task_status["failed_tasks"]) > 50:
                                self.task_status["failed_tasks"] = self.task_status["failed_tasks"][-50:]
                            
                            logger.error(f"Task failed after 3 attempts: {task['id']} - {result.get('error', 'Unknown error')}")
                        else:
                            # Re-queue with lower priority
                            with self.task_lock:
                                self.task_queue.put((priority + 5, task))
                            logger.warning(f"Task failed, re-queuing: {task['id']} - {result.get('error', 'Unknown error')}")
                    
                    self.save_status()
                    self.current_task = None
                
                # Brief pause between tasks
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in background processor: {e}", exc_info=True)
                # Reset current task in case of error
                with self.status_lock:
                    self.current_task = None
                time.sleep(60)
                continue
    
    def _process_conversation_task(self, task):
        """
        Process a conversation summarization task.
        
        Args:
            task: Task data
            
        Returns:
            Result dictionary
        """
        try:
            # Check if LLM is available
            if not self.ai_manager or not self.ai_manager.llm:
                return {"success": False, "error": "LLM not available"}
            
            raw_path = task["data"]["raw_path"]
            output_path = task["data"]["output_path"]
            archive_id = task["data"]["archive_id"]
            
            # Read raw conversation
            with open(raw_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            # Use LLM to structure the conversation
            prompt = f"""You will be analyzing a conversation between a user and GAIA (an AI assistant). 
            Your task is to extract, organize, and structure the most important information from this conversation into a well-formatted markdown document.

            Focus on:
            1. Key facts, concepts, and knowledge shared
            2. Important decisions or conclusions reached
            3. Questions that were thoroughly answered
            4. Any action items or future plans mentioned

            Organize this information into logical sections with clear headers. Do NOT include the entire conversation - only extract the most relevant and useful information.

            The output should be in markdown format and should be structured for easy reference later.

            Here is the conversation to analyze:

            {raw_content}

            Create a structured markdown document from this conversation:"""

            # Generate structured document
            structured_content = self.ai_manager.llm(prompt)
            
            # Ensure the output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save structured content
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(structured_content)
            
            # Extract an improved summary from the structured content
            summary_prompt = f"""Given the following structured analysis of a conversation, 
            provide a concise 2-3 sentence summary that captures the most important points:

            {structured_content[:2000]}  # Limit to first 2000 chars for summary generation

            Summary:"""
            
            improved_summary = self.ai_manager.llm(summary_prompt).strip()
            
            # Update the archive status with the improved summary
            if hasattr(self.ai_manager, 'conversation_manager'):
                self.ai_manager.conversation_manager.update_archive_status(
                    archive_id, 
                    "processed", 
                    improved_summary
                )
            
            return {
                "success": True, 
                "output_path": output_path,
                "improved_summary": improved_summary,
                "message": "Conversation successfully structured"
            }
        except Exception as e:
            logger.error(f"Error processing conversation: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _process_embedding_task(self, task):
        """
        Process a document embedding task.
        
        Args:
            task: Task data
            
        Returns:
            Result dictionary
        """
        try:
            # Check if vector store is available
            if not self.ai_manager or not self.ai_manager.vector_store:
                return {"success": False, "error": "Vector store not available"}
            
            file_path = task["data"]["file_path"]
            
            # Validate file exists
            if not os.path.exists(file_path):
                return {"success": False, "error": f"File not found: {file_path}"}
            
            # Load document
            documents = self.ai_manager.doc_processor.load_and_preprocess_data(
                os.path.dirname(file_path)
            )
            
            # Filter to just the file we want
            filename = os.path.basename(file_path)
            documents = [doc for doc in documents if doc.metadata.get('source', '').endswith(filename)]
            
            if not documents:
                return {"success": False, "error": "Document not found or could not be processed"}
            
            # Update vector store
            updated = self.ai_manager.vector_store_manager.update_vector_store(
                self.ai_manager.vector_store, documents
            )
            
            if not updated:
                return {"success": False, "error": "Failed to update vector store"}
            
            return {
                "success": True,
                "documents_added": len(documents),
                "message": f"Document {filename} successfully embedded"
            }
        except Exception as e:
            logger.error(f"Error embedding document: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _process_lora_task(self, task):
        """
        Process a LoRA fine-tuning task.
        
        Note: This is a placeholder for future implementation as LoRA
        fine-tuning would require additional infrastructure.
        
        Args:
            task: Task data
            
        Returns:
            Result dictionary with placeholder information
        """
        # Note: Actual LoRA implementation would require additional code
        # and infrastructure not included in this example
        logger.info("LoRA fine-tuning task received - this is a placeholder")
        
        try:
            # Check if LoRA is enabled in config
            if not hasattr(self.config, 'BG_ENABLE_LORA') or not self.config.BG_ENABLE_LORA.lower() == 'true':
                return {
                    "success": False,
                    "error": "LoRA fine-tuning is disabled in configuration",
                    "note": "To enable LoRA, set BG_ENABLE_LORA=true in environment"
                }
            
            # For now, just return success with a note
            return {
                "success": True,
                "message": "LoRA fine-tuning placeholder (not yet implemented)",
                "note": "This is a placeholder for future LoRA implementation"
            }
        except Exception as e:
            logger.error(f"Error in LoRA task: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def get_task_status(self, task_id=None):
        """
        Get the status of tasks.
        
        Args:
            task_id: Optional ID of specific task to check
            
        Returns:
            Status information for tasks
        """
        with self.status_lock:
            if task_id:
                # Find the specific task
                for task_list in [self.task_status["pending_tasks"], 
                                self.task_status["completed_tasks"],
                                self.task_status["failed_tasks"]]:
                    for task in task_list:
                        if task["id"] == task_id:
                            return task
                return None
            else:
                # Return overall status
                return {
                    "current_task": self.current_task,
                    "pending_count": len(self.task_status["pending_tasks"]),
                    "completed_count": len(self.task_status["completed_tasks"]),
                    "failed_count": len(self.task_status["failed_tasks"]),
                    "is_processing": self.is_running and self.current_task is not None,
                    "is_idle": self.is_idle(),
                    "last_activity": datetime.fromtimestamp(self.last_activity_time).isoformat()
                }
    
    def cleanup_old_tasks(self, max_completed=100, max_failed=50):
        """
        Clean up old completed and failed tasks.
        
        Args:
            max_completed: Maximum number of completed tasks to keep
            max_failed: Maximum number of failed tasks to keep
        """
        with self.status_lock:
            # Limit completed tasks
            if len(self.task_status["completed_tasks"]) > max_completed:
                # Sort by completion date
                self.task_status["completed_tasks"].sort(
                    key=lambda x: x.get("last_attempt", "")
                )
                # Keep only the most recent ones
                self.task_status["completed_tasks"] = self.task_status["completed_tasks"][-max_completed:]
            
            # Limit failed tasks
            if len(self.task_status["failed_tasks"]) > max_failed:
                # Sort by failure date
                self.task_status["failed_tasks"].sort(
                    key=lambda x: x.get("last_attempt", "")
                )
                # Keep only the most recent ones
                self.task_status["failed_tasks"] = self.task_status["failed_tasks"][-max_failed:]
            
            # Save updated status
            self.save_status()