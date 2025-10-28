"""
Project Manager for organizing conversations into projects.
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path


class ProjectManager:
    """Manages projects and their associated conversations."""
    
    def __init__(self, data_dir: str = "./data"):
        """
        Initialize the project manager.
        
        Args:
            data_dir: Directory to store project data
        """
        self.data_dir = Path(data_dir)
        self.projects_dir = self.data_dir / "projects"
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize projects index
        self.index_file = self.data_dir / "projects_index.json"
        self.projects_index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Load projects index from file."""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"projects": {}}
    
    def _save_index(self):
        """Save projects index to file."""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.projects_index, f, indent=2, ensure_ascii=False)
    
    def create_project(self, name: str, description: str = "") -> str:
        """
        Create a new project.
        
        Args:
            name: Project name
            description: Project description
            
        Returns:
            project_id: Unique identifier for the project
        """
        project_id = f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        project_data = {
            "id": project_id,
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "conversations": []
        }
        
        # Create project directory
        project_dir = self.projects_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Save project metadata
        project_file = project_dir / "project.json"
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        
        # Update index
        self.projects_index["projects"][project_id] = {
            "name": name,
            "description": description,
            "created_at": project_data["created_at"],
            "conversation_count": 0
        }
        self._save_index()
        
        return project_id
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get project details.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Project data dictionary or None if not found
        """
        project_file = self.projects_dir / project_id / "project.json"
        if not project_file.exists():
            return None
        
        with open(project_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all projects.
        
        Returns:
            List of project dictionaries
        """
        projects = []
        for project_id, project_info in self.projects_index["projects"].items():
            projects.append({
                "id": project_id,
                **project_info
            })
        
        # Sort by created_at descending
        projects.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return projects
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete a project and all its conversations.
        
        Args:
            project_id: Project identifier
            
        Returns:
            True if successful, False otherwise
        """
        project_dir = self.projects_dir / project_id
        if not project_dir.exists():
            return False
        
        # Delete all files in project directory
        import shutil
        shutil.rmtree(project_dir)
        
        # Remove from index
        if project_id in self.projects_index["projects"]:
            del self.projects_index["projects"][project_id]
            self._save_index()
        
        return True
    
    def add_conversation(
        self, 
        project_id: str, 
        conversation_id: str,
        title: str = "Untitled Conversation"
    ) -> bool:
        """
        Add a conversation to a project.
        
        Args:
            project_id: Project identifier
            conversation_id: Conversation identifier
            title: Conversation title
            
        Returns:
            True if successful, False otherwise
        """
        project = self.get_project(project_id)
        if not project:
            return False
        
        # Check if conversation already exists
        for conv in project["conversations"]:
            if conv["id"] == conversation_id:
                return False
        
        # Add conversation
        conversation_entry = {
            "id": conversation_id,
            "title": title,
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat()
        }
        
        project["conversations"].append(conversation_entry)
        
        # Save project
        project_file = self.projects_dir / project_id / "project.json"
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project, f, indent=2, ensure_ascii=False)
        
        # Update index
        if project_id in self.projects_index["projects"]:
            self.projects_index["projects"][project_id]["conversation_count"] = len(project["conversations"])
            self._save_index()
        
        return True
    
    def remove_conversation(self, project_id: str, conversation_id: str) -> bool:
        """
        Remove a conversation from a project.
        
        Args:
            project_id: Project identifier
            conversation_id: Conversation identifier
            
        Returns:
            True if successful, False otherwise
        """
        project = self.get_project(project_id)
        if not project:
            return False
        
        # Remove conversation
        project["conversations"] = [
            conv for conv in project["conversations"] 
            if conv["id"] != conversation_id
        ]
        
        # Save project
        project_file = self.projects_dir / project_id / "project.json"
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project, f, indent=2, ensure_ascii=False)
        
        # Delete conversation file
        conv_file = self.projects_dir / project_id / f"{conversation_id}.json"
        if conv_file.exists():
            conv_file.unlink()
        
        # Update index
        if project_id in self.projects_index["projects"]:
            self.projects_index["projects"][project_id]["conversation_count"] = len(project["conversations"])
            self._save_index()
        
        return True
    
    def list_conversations(self, project_id: str) -> List[Dict[str, Any]]:
        """
        List all conversations in a project.
        
        Args:
            project_id: Project identifier
            
        Returns:
            List of conversation dictionaries
        """
        project = self.get_project(project_id)
        if not project:
            return []
        
        # Sort by last_modified descending
        conversations = project.get("conversations", [])
        conversations.sort(key=lambda x: x.get("last_modified", ""), reverse=True)
        return conversations
    
    def save_conversation_to_project(
        self, 
        project_id: str, 
        conversation_id: str,
        conversation_data: Dict[str, Any]
    ) -> bool:
        """
        Save conversation data to a project.
        
        Args:
            project_id: Project identifier
            conversation_id: Conversation identifier
            conversation_data: Conversation data to save
            
        Returns:
            True if successful, False otherwise
        """
        project = self.get_project(project_id)
        if not project:
            return False
        
        # Save conversation file
        conv_file = self.projects_dir / project_id / f"{conversation_id}.json"
        with open(conv_file, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)
        
        # Update conversation metadata in project
        for conv in project["conversations"]:
            if conv["id"] == conversation_id:
                conv["last_modified"] = datetime.now().isoformat()
                break
        
        # Save project
        project_file = self.projects_dir / project_id / "project.json"
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project, f, indent=2, ensure_ascii=False)
        
        return True
    
    def load_conversation_from_project(
        self, 
        project_id: str, 
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load conversation data from a project.
        
        Args:
            project_id: Project identifier
            conversation_id: Conversation identifier
            
        Returns:
            Conversation data or None if not found
        """
        conv_file = self.projects_dir / project_id / f"{conversation_id}.json"
        if not conv_file.exists():
            return None
        
        with open(conv_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_conversation_title(
        self, 
        project_id: str, 
        conversation_id: str, 
        new_title: str
    ) -> bool:
        """
        Update a conversation's title.
        
        Args:
            project_id: Project identifier
            conversation_id: Conversation identifier
            new_title: New title for the conversation
            
        Returns:
            True if successful, False otherwise
        """
        project = self.get_project(project_id)
        if not project:
            return False
        
        # Update conversation title
        for conv in project["conversations"]:
            if conv["id"] == conversation_id:
                conv["title"] = new_title
                conv["last_modified"] = datetime.now().isoformat()
                break
        else:
            return False
        
        # Save project
        project_file = self.projects_dir / project_id / "project.json"
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project, f, indent=2, ensure_ascii=False)
        
        return True
    
    def rename_project(self, project_id: str, new_name: str) -> bool:
        """
        Rename a project.
        
        Args:
            project_id: Project identifier
            new_name: New name for the project
            
        Returns:
            True if successful, False otherwise
        """
        project = self.get_project(project_id)
        if not project:
            return False
        
        project["name"] = new_name
        
        # Save project
        project_file = self.projects_dir / project_id / "project.json"
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project, f, indent=2, ensure_ascii=False)
        
        # Update index
        if project_id in self.projects_index["projects"]:
            self.projects_index["projects"][project_id]["name"] = new_name
            self._save_index()
        
        return True
    
    def search_conversations(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for conversations across all projects.
        
        Args:
            query: Search query
            
        Returns:
            List of matching conversations with project info
        """
        results = []
        query_lower = query.lower()
        
        for project_id in self.projects_index["projects"]:
            project = self.get_project(project_id)
            if not project:
                continue
            
            for conv in project.get("conversations", []):
                # Search in conversation title
                if query_lower in conv.get("title", "").lower():
                    results.append({
                        "project_id": project_id,
                        "project_name": project["name"],
                        "conversation_id": conv["id"],
                        "conversation_title": conv["title"],
                        "last_modified": conv.get("last_modified", "")
                    })
        
        return results
