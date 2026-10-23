"""Database table models.

Import every table model here so ``SQLModel.metadata.create_all`` sees them.
"""

from app.models.internship import (
    Company,
    Department,
    InternshipPosting,
    InternshipApplication,
    ApplicationStatusHistory,
    Placement,
)
from app.models.student_profile import StudentProfile
from app.models.user import User

__all__ = [
    "User",
    "StudentProfile",
    "Company",
    "Department",
    "InternshipPosting",
    "InternshipApplication",
    "ApplicationStatusHistory",
    "Placement",
]
