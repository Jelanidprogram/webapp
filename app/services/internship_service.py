from typing import Optional, List

from app.repositories.internship import InternshipRepository
from app.repositories.student import StudentRepository
from app.schemas.internship import (
    InternshipPostingRead,
    InternshipApplicationRead,
    InternshipApplicationCreate,
    ApplicationStatusHistoryCreate,
    PlacementCreate,
    PlacementRead,
)


class InternshipService:
    """Application rules for the student submission workflow.

    Coordinates the internship and student repositories. Contains no SQL;
    the repositories own persistence.
    """

    def __init__(
        self,
        internship_repo: InternshipRepository,
        student_repo: StudentRepository,
    ):
        self.internship_repo = internship_repo
        self.student_repo = student_repo

    def list_postings(self) -> List[InternshipPostingRead]:
        postings = self.internship_repo.list_active_postings()
        result = []
        for p in postings:
            data = InternshipPostingRead.model_validate(p)
            data.company_name = self.internship_repo.get_company_name(p.company_id)
            data.department_name = self.internship_repo.get_department_name(p.department_id)
            result.append(data)
        return result

    def get_posting(self, posting_id: int) -> Optional[InternshipPostingRead]:
        posting = self.internship_repo.get_posting(posting_id)
        if posting is None:
            return None
        data = InternshipPostingRead.model_validate(posting)
        data.company_name = self.internship_repo.get_company_name(posting.company_id)
        data.department_name = self.internship_repo.get_department_name(posting.department_id)
        return data

    def submit_application(
        self, email: str, posting_id: int
    ) -> Optional[InternshipApplicationRead]:
        """Create an application for the student matched to *email*.

        The student record is created on first use (self-contained workflow)
        so a logged-in user can submit without a separate admin step.
        """
        posting = self.internship_repo.get_posting(posting_id)
        if posting is None or not posting.is_active:
            return None

        student = self.student_repo.get_student_by_email(email)
        if student is None:
            student = self.student_repo.create_student(email)

        application = self.internship_repo.create_application(
            InternshipApplicationCreate(
                student_id=student.student_id,
                posting_id=posting_id,
                status="submitted",
            )
        )
        self.internship_repo.create_status_history(
            ApplicationStatusHistoryCreate(
                application_id=application.application_id,
                status="submitted",
                note="Application submitted by student.",
            )
        )
        return InternshipApplicationRead.model_validate(application)

    # ---------- organization review / match ----------

    def list_applications_for_review(self) -> List[dict]:
        """List all applications with related details for organization review."""
        details = self.internship_repo.list_applications()
        result = []
        for app in details:
            detail = self.internship_repo.get_application_with_details(app.application_id)
            if detail is not None:
                result.append(detail)
        return result

    def create_placement_from_application(
        self,
        application_id: int,
        company_id: int,
        status: str = "matched",
        note: Optional[str] = None,
    ) -> Optional[PlacementRead]:
        """Create a Placement from a selected application.

        Marks the application with the given status and records status history.
        """
        detail = self.internship_repo.get_application_with_details(application_id)
        if detail is None:
            return None

        application = detail["application"]
        placement = self.internship_repo.create_placement(
            PlacementCreate(
                application_id=application.application_id,
                student_id=application.student_id,
                posting_id=application.posting_id,
                company_id=company_id,
                status=status,
            )
        )
        self.internship_repo.update_application_status(
            application_id, status, note or f"Placement {placement.placement_id} created."
        )
        return PlacementRead.model_validate(placement)
