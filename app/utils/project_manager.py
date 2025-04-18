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
        self.projects_dir = os.path.join(os.path.dirname(config.data_path), "projects")
        self.projects_file = os.path.join(self.projects_dir, "projects.json")
        self.current_project = None
        self.projects = {}
        
        # Create projects directory if it doesn't exist
        os.makedirs(self.projects_dir, exist_ok=True)
        
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
        # Create default D&D campaign project
        self.projects["campaign"] = {
            "name": "D&D Campaign",
            "description": "D&D campaign management with GAIA as a roleplaying assistant",
            "instructions_file": "gaia_instructions.txt",
            "data_path": os.path.join(os.path.dirname(self.config.data_path), "campaign-data/core-documentation"),
            "output_path": os.path.join(os.path.dirname(self.config.data_path), "campaign-data/converted_raw"),
            "raw_data_path": os.path.join(os.path.dirname(self.config.data_path), "campaign-data/raw-data"),
            "is_default": True
        }
        
        # Create code analyzer project
        self.projects["code"] = {
            "name": "Code Analyzer",
            "description": "Code analysis and documentation with GAIA as a programming assistant",
            "instructions_file": "code_instructions.txt",
            "data_path": self.config.external_code_path,
            "output_path": os.path.join(os.path.dirname(self.config.data_path), "code-artifacts"),
            "raw_data_path": os.path.join(os.path.dirname(self.config.data_path), "code-raw"),
            "is_default": False
        }
        
        # Save projects
        self.save_projects()
        
        # Create directory structure for projects
        for project_id, project in self.projects.items():
            os.makedirs(project["data_path"], exist_ok=True)
            os.makedirs(project["output_path"], exist_ok=True)
            os.makedirs(project["raw_data_path"], exist_ok=True)
    
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
        self.config.core_instructions_file = os.path.join(self.projects_dir, project["instructions_file"])
        
        logger.info(f"Switched to project: {project['name']}")
        return True
    
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