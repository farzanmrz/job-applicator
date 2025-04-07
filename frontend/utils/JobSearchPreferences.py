import json
import os
from typing import Dict, List, Optional


class JobSearchPreferences:
    """Manages job search preferences and keywords storage."""

    def __init__(self, file_path: str = "data/preferences.json"):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Create preferences file if it doesn't exist."""
        directory = os.path.dirname(self.file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.exists(self.file_path):
            default_data = {
                "education": "",
                "industries": [],
                "countries": [],
                "job_type": [],
                "job_experience": [],
                "technical_skills": [],
                "soft_skills": [],
                "job_titles": [],
            }
            with open(self.file_path, "w") as f:
                json.dump(default_data, f, indent=2)

    def get_preferences(self) -> Dict:
        """Get all saved preferences."""
        with open(self.file_path, "r") as f:
            return json.load(f)

    def save_preferences(self, preferences: Dict) -> None:
        """Save preferences to file."""
        with open(self.file_path, "w") as f:
            json.dump(preferences, f, indent=2)
