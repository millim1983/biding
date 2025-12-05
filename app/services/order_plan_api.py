# 1. 발주계획 API 연동# app/services/order_plan_api.py
from datetime import datetime, timedelta

from typing import Any, Dict, List

import httpx

from app.core.config import get_settings

settings = get_settings()

# app/services/order_plan_api.py
from datetime import datetime, timedelta
from typing import Any, Dict, List

import httpx

from app.core.config import get_settings

settings = get_settings()


async def fetch_order_plan_list(
    page: int = 1,
    num_of_rows: int = 10,
) -> Dict[str, Any]:
    """
    발주계획현황 조회 (getOrderPlanSttusListServc)
    - 조회구분 1 (발주년월/게시일시 기준)
    - 최근 6개월 기준으로 자동 조회
    """

    today = datetime.today()
    six_months_ago = today - timedelta(days=180)

    order_bgn_ym = six_months_ago.strftime("%Y%m")  # 시작: 6개월 전 YYYYMM
    order_end_ym = today.strftime("%Y%m")           # 종료: 이번달 YYYYMM

    params = {
        "numOfRows": num_of_rows,
        "pageNo": page,
        "ServiceKey": settings.publicdata_service_key,
        "type": "json",
        "inqryDiv": 1,              # 1: 발주년월, 게시일시
        "orderBgnYm": order_bgn_ym,
        "orderEndYm": order_end_ym,
        # 필요하면 나중에 inqryBgnDt / inqryEndDt 도 여기 추가
    }

    async with httpx.AsyncClient(
        base_url=settings.order_plan_base_url,
        timeout=15.0,
    ) as client:
        resp = await client.get("/getOrderPlanSttusListServc", params=params)
        resp.raise_for_status()
        data = resp.json()
        return data


def extract_order_plan_items(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    공공데이터 JSON 구조에서 item 리스트만 뽑아주는 함수 (여러 케이스 대응)
    """
    try:
        body = data["response"]["body"]
    except Exception:
        return []

    items = body.get("items")

    # 1) 아예 없으면
    if items is None:
        return []

    # 2) 바로 리스트인 경우: "items": [ {...}, {...} ]
    if isinstance(items, list):
        return items

    # 3) dict인 경우
    if isinstance(items, dict):
        # {"item": [ {...}, {...} ]} 형태
        if "item" in items:
            inner = items["item"]
            if isinstance(inner, list):
                return inner
            if isinstance(inner, dict):
                return [inner]
            return []
        # 그 외에는 dict 하나를 item으로 간주
        return [items]

    # 4) 예상 못한 타입이면 빈 리스트
    return []

def extract_paging_info(data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        body = data["response"]["body"]
        return {
            "numOfRows": body.get("numOfRows", 0),
            "pageNo": body.get("pageNo", 1),
            "totalCount": body.get("totalCount", 0),
        }
    except Exception:
        return {"numOfRows": 0, "pageNo": 1, "totalCount": 0}


from app.core.preferences import Preferences
def filter_order_plans_by_preferences(
    items: List[Dict[str, Any]],
    prefs: Preferences,
) -> List[Dict[str, Any]]:
    """
    관심 기관 / 키워드를 기준으로 발주계획 리스트 필터링
    - 관심 기관이 있으면: orderInsttNm(발주기관명)에 포함되는 것만
    - 키워드가 있으면: bizNm, usgCntnts, specItemNm1~5, specCntnts 중 하나에 포함되는 것만
    - 둘 다 있으면 AND 조건 (기관도, 키워드도 모두 만족)
    """

    orgs = [o.strip() for o in prefs.orgs if o.strip()]
    kws = [k.strip() for k in prefs.keywords if k.strip()]

    if not orgs and not kws:
        # 설정이 하나도 없으면 필터링하지 않고 전체 반환
        return items

    def match_org(it: Dict[str, Any]) -> bool:
        if not orgs:
            return True
        name = (it.get("orderInsttNm") or "") + " " + (it.get("totlmngInsttNm") or "")
        return any(org in name for org in orgs)

    def match_kw(it: Dict[str, Any]) -> bool:
        if not kws:
            return True
        text_fields = [
            it.get("bizNm") or "",
            it.get("usgCntnts") or "",
            it.get("specItemNm1") or "",
            it.get("specItemNm2") or "",
            it.get("specItemNm3") or "",
            it.get("specItemNm4") or "",
            it.get("specItemNm5") or "",
            it.get("specCntnts") or "",
        ]
        blob = " ".join(text_fields)
        return any(kw in blob for kw in kws)

    filtered = [it for it in items if match_org(it) and match_kw(it)]
    return filtered