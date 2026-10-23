from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel


class InternshipPostingBase(SQLModel):
    title: str
    company_id: int
    department_id: int
    description: Optional[str] = None
    is_active: bool = True


class InternshipPostingCreate(InternshipPostingBase):
    pass


class InternshipPostingRead(InternshipPostingBase):
    posting_id: int
    company_name: Optional[str] = None
    department_name: Optional[str] = None


class InternshipApplicationBase(SQLModel):
    student_id: int
    posting_id: int
    status: str = "submitted"


class InternshipApplicationCreate(InternshipApplicationBase):
    pass


class InternshipApplicationRead(InternshipApplicationBase):
    application_id: int
    submitted_at: Optional[datetime] = None


class ApplicationStatusHistoryBase(SQLModel):
    application_id: int
    status: str
    note: Optional[str] = None


class ApplicationStatusHistoryCreate(ApplicationStatusHistoryBase):
    pass


class ApplicationStatusHistoryRead(ApplicationStatusHistoryBase):
    history_id: int
    changed_at: Optional[datetime] = None


class PlacementBase(SQLModel):
    application_id: int
    student_id: int
    posting_id: int
    company_id: int
    status: str = "matched"


class PlacementCreate(PlacementBase):
    pass


class PlacementRead(PlacementBase):
    placement_id: int
    matched_at: Optional[datetime] = None
