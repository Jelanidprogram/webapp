from typing import Optional

from app.repositories.student import StudentRepository
from app.schemas.student import (
    StudentProfileCreate,
    StudentProfileRead,
    StudentProfileUpdate,
)


class StudentService:
    """Application rules for the student workflow.

    Coordinates repositories. Contains no SQL; the repository owns persistence.
    """

    def __init__(self, student_repo: StudentRepository):
        self.student_repo = student_repo

    def _student_for_email(self, email: str) -> Optional:
        student = self.student_repo.get_student_by_email(email)
        if student is None:
            # Self-contained workflow: create the student record on first save so
            # a logged-in user can prepare a profile without a separate admin step.
            student = self.student_repo.create_student(email)
        return student

    def profile_for_email(self, email: str) -> Optional[StudentProfileRead]:
        student = self.student_repo.get_student_by_email(email)
        if student is None:
            return None
        profile = self.student_repo.get_profile_by_student_id(student.student_id)
        if profile is None:
            return None
        return StudentProfileRead.model_validate(profile)

    def save_profile(self, email: str, data: StudentProfileCreate) -> Optional[StudentProfileRead]:
        student = self._student_for_email(email)
        if student is None:
            return None
        profile = self.student_repo.get_profile_by_student_id(student.student_id)
        if profile is None:
            profile = self.student_repo.create_profile(student.student_id, data)
        else:
            update_data = StudentProfileUpdate(
                full_name=data.full_name,
                university_mail=data.university_mail,
                program=data.program,
                year=data.year,
                internship_preference=data.internship_preference,
                resume_cv=data.resume_cv,
            )
            profile = self.student_repo.update_profile(profile, update_data)
        return StudentProfileRead.model_validate(profile)
