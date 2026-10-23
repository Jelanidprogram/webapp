from fastapi import Request
from fastapi.responses import HTMLResponse

from app.dependencies.auth import IsUserLoggedIn, OptionalUserDep
from . import router, templates


@router.get("/", response_class=HTMLResponse, name="index_view")
async def index_view(
    request: Request,
    user_logged_in: IsUserLoggedIn,
    user: OptionalUserDep = None,
):
    return templates.TemplateResponse(
        request=request,
        name="landing.html",
        context={
            "user_logged_in": user_logged_in,
            "user": user,
        },
    )
