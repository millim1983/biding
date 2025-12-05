# app/web/routes_order_plan.py
import math
from fastapi import APIRouter, Query, Request
from fastapi.templating import Jinja2Templates
from app.core.preferences import load_preferences
from app.services.order_plan_api import (
    fetch_order_plan_list,
    extract_order_plan_items,
    extract_paging_info,
    filter_order_plans_by_preferences,  # ★ 추가
)

router = APIRouter(
    prefix="/order-plan",
    tags=["발주계획"],
)

templates = Jinja2Templates(directory="app/templates")




@router.get("/")
async def order_plan_list(
    request: Request,
    page: int = Query(1, ge=1),
):
    from httpx import HTTPStatusError

    prefs = load_preferences()

    try:
        raw = await fetch_order_plan_list(page=page)
        items_all = extract_order_plan_items(raw)
        paging = extract_paging_info(raw)
        items = filter_order_plans_by_preferences(items_all, prefs)
        error_msg = None
    except HTTPStatusError as e:
        items_all = []
        items = []
        paging = {"numOfRows": 0, "pageNo": page, "totalCount": 0}
        error_msg = f"외부 API 오류: {e.response.status_code}"

    # ★ 여기 추가: 전체 페이지 수 계산
    num_of_rows = int(paging.get("numOfRows", 10) or 10)
    total_count = int(paging.get("totalCount", 0) or 0)
    total_pages = max(1, math.ceil(total_count / num_of_rows)) if num_of_rows > 0 else 1


    return templates.TemplateResponse(
        "order_plan_list.html",
        {
            "request": request,
            "items": items,
            "paging": paging,
            "error": error_msg,
            "active_tab": "order-plan",
            "prefs": prefs,
            "original_count": len(items_all),
            "total_pages": total_pages,           # ★ 추가
        },
    )
