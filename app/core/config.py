# app/core/config.py
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# 루트 경로 기준으로 .env 로드
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)

class Settings:
    def __init__(self) -> None:
        self.publicdata_service_key: str | None = os.getenv("PUBLICDATA_SERVICE_KEY")
        self.order_plan_base_url: str = os.getenv(
            "ORDER_PLAN_BASE_URL",
            "https://apis.data.go.kr/1230000/ao/OrderPlanSttusService",
        )

        if not self.publicdata_service_key:
            raise RuntimeError(
                "환경변수 PUBLICDATA_SERVICE_KEY 가 설정되어 있지 않습니다. "
                ".env에 키를 넣었는지 확인하세요."
            )

@lru_cache
def get_settings() -> Settings:
    return Settings()
