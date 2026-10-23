import logging
from datetime import datetime
from typing import Optional, List

from sqlmodel import Session, select

from app.models.internship import (
    InternshipPosting,
    InternshipApplication,
    ApplicationStatusHistory,
    Placement,
    Company,
    Department,
)
from app.models.student_profile import Student, StudentProfile
from app.schemas.internship import (
    InternshipPostingCreate,
    InternshipApplicationCreate,
    ApplicationStatusHistoryCreate,
    PlacementCreate,
)

logger = logging.getLogger(__name__)


class InternshipRepository:
    """Persistence for internship postings, applications, and status history.

    Holds queries/commits only. No business policy lives here.
    """

    def __init__(self, db: Session):
        self.db = db

    # ---------- postings ----------

    def list_active_postings(self) -> List[InternshipPosting]:
        return self.db.exec(
            select(InternshipPosting).where(InternshipPosting.is_active == True)  # noqa: E712
        ).all()

    def get_posting(self, posting_id: int) -> Optional[InternshipPosting]:
        return self.db.get(InternshipPosting, posting_id)

    def get_company_name(self, company_id: int) -> Optional[str]:
        company = self.db.get(Company, company_id)
        return company.name if company else None

    def get_department_name(self, department_id: int) -> Optional[str]:
        department = self.db.get(Department, department_id)
        return department.name if department else None

    def create_posting(self, data: InternshipPostingCreate) -> InternshipPosting:
        posting = InternshipPosting.model_validate(data)
        self.db.add(posting)
        self.db.commit()
        self.db.refresh(posting)
        return posting

    # ---------- applications ----------

    def create_application(
        self, data: InternshipApplicationCreate
    ) -> InternshipApplication:
        application = InternshipApplication.model_validate(data)
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def get_application(self, application_id: int) -> Optional[InternshipApplication]:
        return self.db.get(InternshipApplication, application_id)

    # ---------- status history ----------

    def create_status_history(
        self, data: ApplicationStatusHistoryCreate
    ) -> ApplicationStatusHistory:
        history = ApplicationStatusHistory.model_validate(data)
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    # ---------- applications (organization review) ----------

    def list_applications(self) -> List[InternshipApplication]:
        return self.db.exec(select(InternshipApplication)).all()

    def get_application_with_details(
        self, application_id: int
    ) -> Optional[dict]:
        """Return an application plus its related posting, company, student, and profile."""
        application = self.db.get(InternshipApplication, application_id)
        if application is None:
            return None

        posting = self.db.get(InternshipPosting, application.posting_id)
        company = None
        department = None
        if posting is not None:
            company = self.db.get(Company, posting.company_id)
            department = self.db.get(Department, posting.department_id)

        student = self.db.get(Student, application.student_id)
        profile = None
        if student is not None:
            profile = self.db.exec(
                select(StudentProfile).where(StudentProfile.student_id == student.student_id)
            ).one_or_none()

        return {
            "application": application,
            "posting": posting,
            "company": company,
            "department": department,
            "student": student,
            "profile": profile,
        }

    # ---------- placements ----------

    def list_companies(self) -> List[Company]:
        return self.db.exec(select(Company)).all()

    def create_placement(self, data: PlacementCreate) -> Placement:
        placement = Placement.model_validate(data)
        placement.matched_at = datetime.now()
        self.db.add(placement)
        self.db.commit()
        self.db.refresh(placement)
        return placement

    def get_placement(self, placement_id: int) -> Optional[Placement]:
        return self.db.get(Placement, placement_id)

    def update_application_status(
        self, application_id: int, status: str, note: Optional[str] = None
    ) -> Optional[InternshipApplication]:
        application = self.db.get(InternshipApplication, application_id)
        if application is None:
            return None
        application.status = status
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        self.create_status_history(
            ApplicationStatusHistoryCreate(
                application_id=application_id,
                status=status,
                note=note,
            )
        )
        return application
