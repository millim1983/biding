# app/web/routes_preferences.py
from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status

from app.core.preferences import (
    load_preferences,
    add_keyword,
    delete_keyword,
    add_org,
    delete_org,
)

router = APIRouter(
    prefix="/settings",      # ★ 여기 중요: /settings
    tags=["설정"],
)

templates = Jinja2Templates(directory="app/templates")


@router.get("/preferences")
async def preferences_page(request: Request):
    prefs = load_preferences()
    return templates.TemplateResponse(
        "preferences.html",
        {
            "request": request,
            "prefs": prefs,
            "active_tab": "settings",
        },
    )


@router.post("/preferences/keywords/add")
async def add_keyword_action(keyword: str = Form(...)):
    add_keyword(keyword)
    return RedirectResponse(
        url="/settings/preferences", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/preferences/keywords/delete")
async def delete_keyword_action(keyword: str = Form(...)):
    delete_keyword(keyword)
    return RedirectResponse(
        url="/settings/preferences", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/preferences/orgs/add")
async def add_org_action(org_name: str = Form(...)):
    add_org(org_name)
    return RedirectResponse(
        url="/settings/preferences", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/preferences/orgs/delete")
async def delete_org_action(org_name: str = Form(...)):
    delete_org(org_name)
    return RedirectResponse(
        url="/settings/preferences", status_code=status.HTTP_303_SEE_OTHER
    )
