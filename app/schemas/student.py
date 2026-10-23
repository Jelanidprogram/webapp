from typing import Optional

from sqlmodel import SQLModel


class StudentProfileBase(SQLModel):
    full_name: Optional[str] = None
    university_mail: Optional[str] = None
    program: Optional[str] = None
    year: Optional[int] = None
    internship_preference: Optional[str] = None
    resume_cv: Optional[str] = None


class StudentProfileCreate(StudentProfileBase):
    full_name: str
    program: str
    year: int


class StudentProfileUpdate(StudentProfileBase):
    pass


class StudentProfileRead(StudentProfileBase):
    profile_id: int
    student_id: int
