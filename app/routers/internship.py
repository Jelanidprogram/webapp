from fastapi import Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies import SessionDep
from app.dependencies.auth import AuthDep, AdminDep
from app.repositories.internship import InternshipRepository
from app.repositories.student import StudentRepository
from app.services.internship_service import InternshipService
from app.schemas.internship import PlacementCreate
from app.utilities.flash import flash

from . import router, templates


@router.get("/internship/postings", response_class=HTMLResponse, name="internship_postings_view")
async def internship_postings_view(
    request: Request,
    db: SessionDep,
    user: AuthDep,
):
    """List available internship postings for the student to apply to."""
    service = InternshipService(InternshipRepository(db), StudentRepository(db))
    postings = service.list_postings()
    return templates.TemplateResponse(
        request=request,
        name="internship/postings.html",
        context={"user": user, "postings": postings},
    )


@router.get("/internship/apply/{posting_id}", response_class=HTMLResponse, name="internship_apply_view")
async def internship_apply_view(
    request: Request,
    db: SessionDep,
    user: AuthDep,
    posting_id: int,
):
    """Show a posting's details and the application submission form."""
    service = InternshipService(InternshipRepository(db), StudentRepository(db))
    posting = service.get_posting(posting_id)
    if posting is None:
        flash(request, "Internship posting not found.", "danger")
        return RedirectResponse(
            url=request.url_for("internship_postings_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return templates.TemplateResponse(
        request=request,
        name="internship/apply.html",
        context={"user": user, "posting": posting},
    )


@router.post("/internship/applications", response_class=HTMLResponse, name="internship_application_submit")
async def internship_application_submit(
    request: Request,
    db: SessionDep,
    user: AuthDep,
    posting_id: int = Form(...),
):
    """Submit an application to the selected posting."""
    service = InternshipService(InternshipRepository(db), StudentRepository(db))
    application = service.submit_application(user.email, posting_id)
    if application is None:
        flash(
            request,
            "Could not submit the application. The posting may be inactive.",
            "danger",
        )
        return RedirectResponse(
            url=request.url_for("internship_postings_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    flash(request, "Application submitted.", "success")
    return RedirectResponse(
        url=request.url_for("internship_submitted_view", application_id=application.application_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/internship/applications/{application_id}", response_class=HTMLResponse, name="internship_submitted_view")
async def internship_submitted_view(
    request: Request,
    db: SessionDep,
    user: AuthDep,
    application_id: int,
):
    """Show the submission confirmation for an application."""
    service = InternshipService(InternshipRepository(db), StudentRepository(db))
    application = InternshipRepository(db).get_application(application_id)
    if application is None:
        flash(request, "Application not found.", "danger")
        return RedirectResponse(
            url=request.url_for("internship_postings_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return templates.TemplateResponse(
        request=request,
        name="internship/submitted.html",
        context={"user": user, "application": application},
    )


# ---------- organization: review / match ----------

@router.get(
    "/organization/applications",
    response_class=HTMLResponse,
    name="organization_applications_view",
)
async def organization_applications_view(
    request: Request,
    db: SessionDep,
    user: AdminDep,
):
    """List all applications for organization review and matching."""
    service = InternshipService(InternshipRepository(db), StudentRepository(db))
    applications = service.list_applications_for_review()
    return templates.TemplateResponse(
        request=request,
        name="organization/applications.html",
        context={"user": user, "applications": applications},
    )


@router.get(
    "/organization/applications/{application_id}",
    response_class=HTMLResponse,
    name="organization_application_detail_view",
)
async def organization_application_detail_view(
    request: Request,
    db: SessionDep,
    user: AdminDep,
    application_id: int,
):
    """Show a single application's details and the placement creation form."""
    service = InternshipService(InternshipRepository(db), StudentRepository(db))
    detail = service.internship_repo.get_application_with_details(application_id)
    if detail is None:
        flash(request, "Application not found.", "danger")
        return RedirectResponse(
            url=request.url_for("organization_applications_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    companies = service.internship_repo.list_companies()
    return templates.TemplateResponse(
        request=request,
        name="organization/application_detail.html",
        context={
            "user": user,
            "application": detail["application"],
            "posting": detail["posting"],
            "company": detail["company"],
            "department": detail["department"],
            "student": detail["student"],
            "profile": detail["profile"],
            "companies": companies,
        },
    )


@router.post(
    "/organization/placements",
    response_class=HTMLResponse,
    name="organization_placement_create",
)
async def organization_placement_create(
    request: Request,
    db: SessionDep,
    user: AdminDep,
    application_id: int = Form(...),
    company_id: int = Form(...),
    status: str = Form("matched"),
    note: str = Form(""),
):
    """Create a Placement from a selected application."""
    service = InternshipService(InternshipRepository(db), StudentRepository(db))
    placement = service.create_placement_from_application(
        application_id,
        company_id,
        status=status,
        note=note or None,
    )
    if placement is None:
        flash(request, "Could not create placement. Application not found.", "danger")
        return RedirectResponse(
            url=request.url_for("organization_applications_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    flash(
        request,
        f"Placement #{placement.placement_id} created and application marked {placement.status}.",
        "success",
    )
    return RedirectResponse(
        url=request.url_for("organization_application_detail_view", application_id=application_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )
