"""
This file defines the Pydantic output models for extractor agents.
Naming: Out(put)Ext(raction)Edu(cation)
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class OutExtEdu(BaseModel):
    class OutExtEduLvl(str, Enum):
        HS = "Highschool"
        Assoc = "Associate"
        UG = "Undergraduate"
        PG = "Postgraduate"
        PhD = "Doctoral"
        PD = "Postdoctoral"

    class OutExtEduStat(str, Enum):
        Complete = "Complete"
        Ongoing = "Ongoing"

    class OutExtEduResp(BaseModel):
        ed_lvl: "OutExtEdu.OutExtEduLvl"
        ed_org: str
        ed_degree: str
        ed_startdate: Optional[str]
        ed_enddate: Optional[str]
        ed_status: "OutExtEdu.OutExtEduStat"
        ed_majors: List[str]
        ed_minors: List[str]
        ed_location: str
        ed_gpa: Optional[float]

    education: list[OutExtEduResp]
