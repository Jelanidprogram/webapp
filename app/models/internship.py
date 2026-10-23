from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Company(SQLModel, table=True):
    """An organization offering internship placements."""

    company_id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = Field(default=None)


class Department(SQLModel, table=True):
    """A department within a company that approves placements."""

    department_id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.company_id", index=True)
    name: str = Field(index=True)
    description: Optional[str] = Field(default=None)


class InternshipPosting(SQLModel, table=True):
    """An advertised internship position posted by a company/department."""

    posting_id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    company_id: int = Field(foreign_key="company.company_id")
    department_id: int = Field(foreign_key="department.department_id")
    description: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)


class InternshipApplication(SQLModel, table=True):
    """A student's application to an internship posting."""

    application_id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.student_id", index=True)
    posting_id: int = Field(foreign_key="internshipposting.posting_id", index=True)
    status: str = Field(default="submitted", index=True)
    submitted_at: Optional[datetime] = Field(default=None)


class ApplicationStatusHistory(SQLModel, table=True):
    """An audit trail of status changes for an application."""

    history_id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="internshipapplication.application_id", index=True)
    status: str = Field(index=True)
    changed_at: Optional[datetime] = Field(default=None)
    note: Optional[str] = Field(default=None)


class Placement(SQLModel, table=True):
    """A placement created from a selected application by the organization."""

    placement_id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="internshipapplication.application_id", index=True)
    student_id: int = Field(foreign_key="student.student_id", index=True)
    posting_id: int = Field(foreign_key="internshipposting.posting_id", index=True)
    company_id: int = Field(foreign_key="company.company_id", index=True)
    status: str = Field(default="matched", index=True)
    matched_at: Optional[datetime] = Field(default=None)
