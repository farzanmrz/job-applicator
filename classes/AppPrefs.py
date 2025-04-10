import json
import os
import importlib
from typing import Dict, List, Optional


class AppPrefs:
    """Manages job search preferences and keywords storage."""

    def __init__(self, file_path: str = "data/prefsaved.json"):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self) -> None:
        """Create preferences file if it doesn't exist."""
        directory = os.path.dirname(self.file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.exists(self.file_path):
            default_data = {
                "education": "",
                "industries": [],
                "locations": [],
                "job_type": [],
                "job_experience": [],
                "technical_skills": [],
                "soft_skills": [],
                "job_titles": [],
                "modality": [],
                "availability": "Flexible"
            }
            with open(self.file_path, "w") as f:
                json.dump(default_data, f, indent=2)

    def get_prefs(self) -> Dict:
        """Get all saved preferences."""
        with open(self.file_path, "r") as f:
            return json.load(f)

    def save_prefs(self, preferences: Dict) -> None:
        """Save preferences to file."""
        with open(self.file_path, "w") as f:
            json.dump(preferences, f, indent=2)