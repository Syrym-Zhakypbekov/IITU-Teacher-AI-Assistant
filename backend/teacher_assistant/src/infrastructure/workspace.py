import os
import json
from typing import List, Dict
from .database import VectorDatabase

class WorkspaceManager:
    """
    Core Infrastructure for Multi-Teacher Isolation.
    Ensures each teacher has a physically separate database and storage space.
    """
    def __init__(self, base_dir="./storage"):
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)
        self._db_cache = {}
        self._mounted_dbs = {} # Store external mounts {id: {path, metadata}}

    def get_teacher_path(self, teacher_id: str) -> str:
        """Generates and ensures a unique directory for a teacher."""
        teacher_path = os.path.join(self.base_dir, f"teacher_{teacher_id}")
        os.makedirs(teacher_path, exist_ok=True)
        return teacher_path

    def save_metadata(self, teacher_id: str, metadata: Dict):
        """Saves course metadata inside the isolated workspace."""
        path = os.path.join(self.get_teacher_path(teacher_id), "metadata.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def get_metadata(self, teacher_id: str) -> Dict:
        """Loads course metadata from the isolated workspace."""
        path = os.path.join(self.get_teacher_path(teacher_id), "metadata.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"id": teacher_id, "subject": "Unknown", "teacherName": "Unknown"}

    def list_workspaces(self) -> List[Dict]:
        """Discovers all existing teacher workspaces and their metadata."""
        workspaces = []
        if not os.path.exists(self.base_dir):
            return []
            
        for entry in os.listdir(self.base_dir):
            if entry.startswith("teacher_"):
                teacher_id = entry.replace("teacher_", "")
                # Skip if this ID is masked by a mount (unlikely but safe)
                if teacher_id in self._mounted_dbs: continue
                
                meta = self.get_metadata(teacher_id)
                # Ensure ID is consistent
                meta["id"] = teacher_id
                workspaces.append(meta)
        
        # Append mounted workspaces
        for mid, mdata in self._mounted_dbs.items():
            workspaces.append(mdata['metadata'])
            
        return workspaces

    def mount_database(self, course_id: str, db_path: str, metadata: Dict):
        """Mounts an existing external LanceDB as a workspace."""
        self._mounted_dbs[course_id] = {
            "path": os.path.abspath(db_path),
            "metadata":  {**metadata, "id": course_id, "is_mounted": True}
        }

    def get_cache_path(self, teacher_id: str) -> str:
        """Returns isolated cache path for the teacher."""
        return os.path.join(self.get_teacher_path(teacher_id), "smart_cache.db")

    def get_database(self, teacher_id: str) -> VectorDatabase:
        """Returns an isolated VectorDatabase instance for the teacher."""
        if teacher_id in self._db_cache:
            return self._db_cache[teacher_id]

        if teacher_id in self._db_cache:
            return self._db_cache[teacher_id]

        # Check mounts first
        if teacher_id in self._mounted_dbs:
             db_path = self._mounted_dbs[teacher_id]["path"]
        else:
             db_path = os.path.join(self.get_teacher_path(teacher_id), "vector_db")
             
        db_instance = VectorDatabase(db_path=db_path)
        
        self._db_cache[teacher_id] = db_instance
        return db_instance
