# state.py (Conceptual Example for Scalability)
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class JobState(BaseModel):
    """
    Represents the shared state - designed for scalability with multiple platforms.
    """

    # State level variables
    current_action: Optional[Literal["job_prof", "job_srch", "job_apply", "idle"]] = (
        "discover_jobs"
    )
    msgs: List[str] = []
    plat_auth_status: Dict[str, bool] = Field(default_factory=dict)
    plat_sesh_info: Dict[str, Any] = Field(default_factory=dict)
    plats_srch: List[str] = Field(default_factory=list)
    scraped_jobs: List[Dict[str, Any]] = Field(default_factory=list)
