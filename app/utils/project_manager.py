"""
Project Manager module for GAIA Assistant.
Handles project profiles, switching, and instruction management.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List

# Get the logger
logger = logging.getLogger("GAIA")

class ProjectManager:
    """Manages different project profiles for GAIA."""
    
    def __init__(self, config):
        """
        Initialize with configuration.
        
        Args:
            config: Configuration object
        """
        self.config = config
        
        # Use projects_dir from config or default to /app/shared
        self.projects_dir = getattr(config, 'projects_dir', '/app/shared')
        
        # Projects file now in shared directory
        self.projects_file = os.path.join(self.projects_dir, "projects.json")
        self.current_project = None
        self.projects = {}
        
        # Create directories
        os.makedirs(self.projects_dir, exist_ok=True)
        os.makedirs(os.path.join(self.projects_dir, "instructions"), exist_ok=True)
        
        # Load projects
        self.load_projects()
        
        # Load default project
        self.load_default_project()

    
    def load_projects(self) -> None:
        """Load projects from the projects file."""
        if os.path.exists(self.projects_file):
            try:
                with open(self.projects_file, 'r', encoding='utf-8') as f:
                    self.projects = json.load(f)
                logger.info(f"Loaded {len(self.projects)} projects")
            except Exception as e:
                logger.error(f"Error loading projects: {e}")
                self.projects = {}
                self.create_default_projects()
        else:
            logger.info("No projects file found, creating defaults")
            self.create_default_projects()
    
    def create_default_projects(self) -> None:
        """Create default projects if none exist."""
        # Create default user context (Personal Assistant)
        self.projects["default"] = {
            "name": "Personal Assistant",
            "description": "Real-world applications for the user Doru",
            "instructions_file": "instructions/default_instructions.txt",
            "data_path": os.path.join(self.projects_dir, "../projects/default/core-documentation"),
            "output_path": os.path.join(self.projects_dir, "../projects/default/converted_raw"),
            "raw_data_path": os.path.join(self.projects_dir, "../projects/default/raw-data"),
            "archives_dir": os.path.join(self.projects_dir, "../projects/default/conversation_archives"),
            "structured_archives_dir": os.path.join(self.projects_dir, "../projects/default/structured_archives"),
            "is_default": True,
            "icon": "user",
            "vector_db_subdir": "default"
        }
        
        # Create D&D gaming context
        self.projects["dnd"] = {
            "name": "D&D Gaming Assistant",
            "description": "Gaming context for Rupert Roads",
            "instructions_file": "instructions/dnd_instructions.txt",
            "data_path": os.path.join(self.projects_dir, "../projects/dnd-campaign/core-documentation"),
            "output_path": os.path.join(self.projects_dir, "../projects/dnd-campaign/converted_raw"),
            "raw_data_path": os.path.join(self.projects_dir, "../projects/dnd-campaign/raw-data"),
            "archives_dir": os.path.join(self.projects_dir, "../projects/dnd-campaign/conversation_archives"),
            "structured_archives_dir": os.path.join(self.projects_dir, "../projects/dnd-campaign/structured_archives"),
            "is_default": False,
            "icon": "dice-d20",
            "vector_db_subdir": "dnd"
        }
        
        # Create code analyzer context
        self.projects["code"] = {
            "name": "Code Assistant",
            "description": "Programming and code review assistance",
            "instructions_file": "instructions/code_instructions.txt",
            "data_path": os.path.join(self.projects_dir, "../projects/code-assistant/core-documentation"),
            "output_path": os.path.join(self.projects_dir, "../projects/code-assistant/output"),
            "raw_data_path": os.path.join(self.projects_dir, "../projects/code-assistant/raw"),
            "archives_dir": os.path.join(self.projects_dir, "../projects/code-assistant/conversation_archives"),
            "structured_archives_dir": os.path.join(self.projects_dir, "../projects/code-assistant/structured_archives"),
            "is_default": False,
            "icon": "code",
            "vector_db_subdir": "code",
            "model_type": "code"  # Flag to indicate this project needs the code model
        }
        
        # Save projects
        self.save_projects()
        
        # Create directory structure for projects
        for project_id, project in self.projects.items():
            os.makedirs(project["data_path"], exist_ok=True)
            os.makedirs(project["output_path"], exist_ok=True)
            os.makedirs(project["raw_data_path"], exist_ok=True)
            os.makedirs(project["archives_dir"], exist_ok=True)
            os.makedirs(project["structured_archives_dir"], exist_ok=True)
        
    def save_projects(self) -> None:
        """Save projects to the projects file."""
        try:
            with open(self.projects_file, 'w', encoding='utf-8') as f:
                json.dump(self.projects, f, indent=2)
            logger.info(f"Saved {len(self.projects)} projects")
        except Exception as e:
            logger.error(f"Error saving projects: {e}")
    
    def load_default_project(self) -> None:
        """Load the default project."""
        for project_id, project in self.projects.items():
            if project.get("is_default", False):
                self.switch_project(project_id)
                return
        
        # If no default project, use the first one
        if self.projects:
            first_project_id = next(iter(self.projects))
            self.switch_project(first_project_id)
    
    def switch_project(self, project_id: str) -> bool:
        """
        Switch to a different project.
        
        Args:
            project_id: ID of the project to switch to
            
        Returns:
            True if successful, False otherwise
        """
        if project_id not in self.projects:
            logger.error(f"Project {project_id} not found")
            return False
        
        project = self.projects[project_id]
        
        # Update current project
        self.current_project = project_id
        
        # Update configuration
        self.config.data_path = project["data_path"]
        self.config.output_path = project["output_path"]
        self.config.raw_data_path = project["raw_data_path"]
        
        
        # If the instructions_file is an absolute path, use it directly
        if os.path.isabs(project["instructions_file"]):
            self.config.core_instructions_file = project["instructions_file"]
        else:
            # Otherwise, join it with the projects directory
            self.config.core_instructions_file = os.path.join(self.projects_dir, project["instructions_file"])
        
        # Update vector database path more explicitly
        vector_db_subdir = project.get("vector_db_subdir", project_id)
        self.config.vector_db_path = os.path.join(self.projects_dir, "chroma_db", vector_db_subdir)
        
        # Ensure directory exists
        os.makedirs(self.config.vector_db_path, exist_ok=True)
        
        # Set model type if specified
        if "model_type" in project:
            self.config.model_type = project["model_type"]
        else:
            self.config.model_type = "default"
        
        logger.info(f"Switched to project: {project['name']}")
        return True
    
    def get_context_dirs(self, project_id=None):
        """
        Get context-specific directories for a project.
        
        Args:
            project_id: ID of the project, or None for current project
            
        Returns:
            Dictionary with context-specific directories
        """
        if project_id is None:
            project_id = self.current_project
            
        if project_id not in self.projects:
            logger.error(f"Project {project_id} not found")
            return {}
            
        project = self.projects[project_id]
        
        return {
            "data_path": project["data_path"],
            "output_path": project["output_path"],
            "raw_data_path": project["raw_data_path"],
            "archives_dir": project["archives_dir"],
            "structured_archives_dir": project["structured_archives_dir"],
            "vector_db_path": os.path.join(os.path.dirname(self.config.vector_db_path), "shared/chroma_db", 
                                        project.get("vector_db_subdir", project_id))
        }
    
    def create_project(self, project_id: str, project_data: Dict[str, Any]) -> bool:
        """
        Create a new project.
        
        Args:
            project_id: ID for the new project
            project_data: Dictionary with project data
            
        Returns:
            True if successful, False otherwise
        """
        if project_id in self.projects:
            logger.error(f"Project {project_id} already exists")
            return False
        
        required_fields = ["name", "description", "instructions_file"]
        if not all(field in project_data for field in required_fields):
            logger.error("Missing required fields for project")
            return False
        
        # Set default paths if not provided
        if "data_path" not in project_data:
            project_data["data_path"] = os.path.join(self.projects_dir, project_id, "data")
        if "output_path" not in project_data:
            project_data["output_path"] = os.path.join(self.projects_dir, project_id, "output")
        if "raw_data_path" not in project_data:
            project_data["raw_data_path"] = os.path.join(self.projects_dir, project_id, "raw")
        
        # Create directory structure
        os.makedirs(project_data["data_path"], exist_ok=True)
        os.makedirs(project_data["output_path"], exist_ok=True)
        os.makedirs(project_data["raw_data_path"], exist_ok=True)
        
        # Add project
        self.projects[project_id] = project_data
        
        # Save projects
        self.save_projects()
        
        logger.info(f"Created new project: {project_data['name']}")
        return True
    
    def update_project(self, project_id: str, project_data: Dict[str, Any]) -> bool:
        """
        Update an existing project.
        
        Args:
            project_id: ID of the project to update
            project_data: Dictionary with updated project data
            
        Returns:
            True if successful, False otherwise
        """
        if project_id not in self.projects:
            logger.error(f"Project {project_id} not found")
            return False
        
        # Update project data
        self.projects[project_id].update(project_data)
        
        # Save projects
        self.save_projects()
        
        logger.info(f"Updated project: {self.projects[project_id]['name']}")
        return True
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project.
        
        Args:
            project_id: ID of the project to delete
            
        Returns:
            True if successful, False otherwise
        """
        if project_id not in self.projects:
            logger.error(f"Project {project_id} not found")
            return False
        
        # Check if it's the default project
        if self.projects[project_id].get("is_default", False):
            logger.error("Cannot delete the default project")
            return False
        
        # Delete project
        project_name = self.projects[project_id]["name"]
        del self.projects[project_id]
        
        # Save projects
        self.save_projects()
        
        logger.info(f"Deleted project: {project_name}")
        return True
    
    def get_project_instructions(self, project_id: Optional[str] = None) -> str:
        """
        Get the instructions for a project.
        
        Args:
            project_id: ID of the project, or None for current project
            
        Returns:
            Project instructions as a string
        """
        if project_id is None:
            project_id = self.current_project
        
        if project_id not in self.projects:
            logger.error(f"Project {project_id} not found")
            return ""
        
        instructions_file = os.path.join(self.projects_dir, self.projects[project_id]["instructions_file"])
        
        try:
            with open(instructions_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading instructions file: {e}")
            return ""
    
    def get_user_context(self, project_id=None):
        """
        Get user-specific context information for the given project.
        
        Args:
            project_id: ID of the project, or None for current project
            
        Returns:
            Dictionary with user context information
        """
        if project_id is None:
            project_id = self.current_project
            
        if project_id not in self.projects:
            return {"user_name": "user", "relation": "assistant"}
            
        # Get project data
        project = self.projects[project_id]
        
        # Default context
        context = {
            "user_name": "user",
            "relation": "assistant",
            "greeting": "Hello",
            "style": "helpful and conversational"
        }
        
        # Override with project-specific settings if available
        if "user_context" in project:
            context.update(project["user_context"])
        else:
            # Legacy support for existing projects
            if project_id == "dnd":
                context = {
                    "user_name": "Rupert",
                    "relation": "integrated AI",
                    "greeting": "Systems online",
                    "style": "technical but supportive",
                    "perspective_phrases": ["my Warforged frame", "my artifice", "my mission"]
                }
            elif project_id == "code":
                context = {
                    "user_name": "developer",
                    "relation": "code assistant",
                    "greeting": "Ready to assist",
                    "style": "technical and precise"
                }
            else:  # default
                context = {
                    "user_name": "Doru",
                    "relation": "personal assistant",
                    "greeting": "Hello",
                    "style": "helpful and conversational"
                }
            
            # Cache the context for future use
            self.projects[project_id]["user_context"] = context
            self.save_projects()
        
        # Add relation description for AI
        if "relation_description" not in context:
            if context["relation"] == "integrated AI":
                context["relation_description"] = f"You are an AI integrated into {context['user_name']}'s systems."
            elif context["relation"] == "assistant":
                context["relation_description"] = f"You are a helpful assistant for {context['user_name']}."
            else:
                context["relation_description"] = f"You are a {context['relation']} for {context['user_name']}."
        
        return context
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """
        Get a list of all projects.
        
        Returns:
            List of project dictionaries with summary information
        """
        result = []
        for project_id, project in self.projects.items():
            result.append({
                "id": project_id,
                "name": project["name"],
                "description": project["description"],
                "is_default": project.get("is_default", False),
                "is_current": project_id == self.current_project
            })
        
        return result
    
    def get_current_project(self) -> Dict[str, Any]:
        """
        Get information about the current project.
        
        Returns:
            Dictionary with current project information
        """
        if not self.current_project or self.current_project not in self.projects:
            return {}
        
        project = self.projects[self.current_project].copy()
        project["id"] = self.current_project
        return project