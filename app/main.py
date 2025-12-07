
#FastAPI 메인 진입점
# # app/main.py
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.web.routes_order_plan import router as order_plan_router
from app.web.routes_preferences import router as preferences_router  # ★ 추가
# from app.web.routes_admin import router as admin_router

app = FastAPI(title="비딩앱 - 발주/입찰 추적 서비스")

# 정적 파일 (선택사항)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 1. 발주계획 라우터 등록
app.include_router(order_plan_router)
app.include_router(preferences_router)  # ★ 기관 키워드 설정
# app.include_router(admin_router)

@app.get("/")
async def root():
    # 처음 접속하면 발주계획 리스트로 이동
    return RedirectResponse(url="/order-plan/")



