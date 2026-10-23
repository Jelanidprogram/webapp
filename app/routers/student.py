import uuid
from pathlib import Path

from fastapi import File, Form, Request, status, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies import SessionDep
from app.dependencies.auth import AuthDep
from app.schemas.student import StudentProfileCreate
from app.repositories.student import StudentRepository
from app.services.student_service import StudentService
from app.utilities.flash import flash

from . import router, templates

RESUME_UPLOAD_DIR = Path("app/static/uploads/resumes")


def _save_resume_file(resume_cv: UploadFile) -> str:
    """Persist an uploaded resume file and return a path served under /static."""
    RESUME_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    ext = Path(resume_cv.filename or "").suffix
    safe_name = f"{uuid.uuid4().hex}{ext}"
    dest = RESUME_UPLOAD_DIR / safe_name
    contents = resume_cv.file.read()
    dest.write_bytes(contents)
    return f"uploads/resumes/{safe_name}"


@router.get("/student/profile", response_class=HTMLResponse, name="student_profile_view")
async def student_profile_view(
    request: Request,
    db: SessionDep,
    user: AuthDep,
):
    """View the student's prepared internship-application profile."""
    service = StudentService(StudentRepository(db))
    profile = service.profile_for_email(user.email)
    return templates.TemplateResponse(
        request=request,
        name="student/profile.html",
        context={"user": user, "profile": profile},
    )


@router.post("/student/profile", response_class=HTMLResponse, name="student_profile_save")
async def student_profile_save(
    request: Request,
    db: SessionDep,
    user: AuthDep,
    full_name: str = Form(...),
    program: str = Form(...),
    year: int = Form(...),
    university_mail: str = Form(""),
    internship_preference: str = Form(""),
    resume_cv: UploadFile = File(None),
):
    """Create or update the student's profile (prepare internship application).

    resume_cv is only updated when a new file is uploaded; otherwise the existing
    file is left untouched.
    """
    service = StudentService(StudentRepository(db))
    kwargs = {
        "full_name": full_name,
        "program": program,
        "year": year,
        "university_mail": university_mail or None,
        "internship_preference": internship_preference or None,
    }
    if resume_cv is not None:
        kwargs["resume_cv"] = _save_resume_file(resume_cv)
    data = StudentProfileCreate(**kwargs)
    profile = service.save_profile(user.email, data)
    if profile is None:
        flash(
            request,
            "Your account could not be linked to a student record.",
            "danger",
        )
        return RedirectResponse(
            url=request.url_for("student_profile_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    flash(request, "Profile saved.", "success")
    return RedirectResponse(
        url=request.url_for("student_profile_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
