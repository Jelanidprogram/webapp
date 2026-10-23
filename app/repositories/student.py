import logging
from typing import Optional

from sqlmodel import Session, select

from app.models.student_profile import Student, StudentProfile
from app.schemas.student import StudentProfileCreate, StudentProfileUpdate

logger = logging.getLogger(__name__)


class StudentRepository:
    """Persistence for student records.

    Holds queries/commits only. No business policy lives here.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_student_by_email(self, email: str) -> Optional[Student]:
        return self.db.exec(
            select(Student).where(Student.email == email)
        ).one_or_none()

    def create_student(self, email: str) -> Student:
        student = Student(email=email)
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def get_profile_by_student_id(self, student_id: int) -> Optional[StudentProfile]:
        return self.db.exec(
            select(StudentProfile).where(StudentProfile.student_id == student_id)
        ).one_or_none()

    def create_profile(
        self, student_id: int, data: StudentProfileCreate
    ) -> StudentProfile:
        profile = StudentProfile(
            student_id=student_id,
            FullName=data.full_name,
            UniversityMail=data.university_mail,
            Program=data.program,
            Year=data.year,
            InternshipPreference=data.internship_preference,
            resume_cv=data.resume_cv,
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update_profile(
        self, profile: StudentProfile, data: StudentProfileUpdate
    ) -> StudentProfile:
        payload = data.model_dump(exclude_unset=True)
        field_map = {
            "full_name": "FullName",
            "university_mail": "UniversityMail",
            "program": "Program",
            "year": "Year",
            "internship_preference": "InternshipPreference",
            "resume_cv": "resume_cv",
        }
        for schema_field, model_field in field_map.items():
            if schema_field in payload:
                setattr(profile, model_field, payload[schema_field])
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile
