# app/web/routes_admin.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.services.order_plan_sync import (
    sync_order_plan_recent,
    sync_order_plan_december_sample,  # ← 이 줄 추가
)


# ★ main.py에서 'router'를 import하기 때문에 이름이 꼭 'router'여야 함
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


@router.post("/sync/order-plan")
async def admin_sync_order_plan():
    """
    발주계획 동기화:
    - 발주시기 기준 과거 1개월 ~ 향후 3개월
    - 나라장터 API에서 가져와 order_plan 테이블에 upsert
    """
    await sync_order_plan_recent()
    return JSONResponse({"status": "ok", "message": "order_plan sync finished"})

@router.post("/sync/order-plan-dec-sample")
async def admin_sync_order_plan_dec_sample():
    """
    테스트용:
    - 올해 12월 발주시기 건
    - 최대 100건만 DB에 저장
    """
    await sync_order_plan_december_sample()
    return JSONResponse({"status": "ok", "message": "order_plan december sample sync finished"})
