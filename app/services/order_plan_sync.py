# app/services/order_plan_sync.py

from datetime import datetime
from dateutil.relativedelta import relativedelta  # pip install python-dateutil
import math
from typing import Optional

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.order_plan import OrderPlan
from app.services.order_plan_api import (
    fetch_order_plan_search_page,
    extract_order_plan_items_from_search,
    extract_paging_from_search,
)
# from app.crud.order_plan import upsert_order_plan


def _parse_int(value: Optional[str]) -> Optional[int]:
    try:
        if value is None or value == "":
            return None
        return int(value)
    except (ValueError, TypeError):
        return None


def _parse_numeric(value: Optional[str]):
    try:
        if value is None or value == "":
            return None
        return int(value)  # 일단 정수로 저장 (원화)
    except (ValueError, TypeError):
        return None


def _parse_dt(value: Optional[str]):
    # 예: "2016-06-22 10:32:00"
    try:
        if not value:
            return None
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None


def upsert_order_plan(
    db: Session,
    item: dict,
    source_api: str = "getOrderPlanSttusListServcPPSSrch",
):
    op = (
        db.query(OrderPlan)
        .filter(OrderPlan.order_plan_unty_no == item.get("orderPlanUntyNo"))
        .first()
    )

    if not op:
        op = OrderPlan(order_plan_unty_no=item.get("orderPlanUntyNo"))
        db.add(op)

    # 🔹 연도/월/연월 세팅
    year_raw = item.get("orderYear")      # 예: "2025" 또는 2025
    month_raw = item.get("orderMnth")     # 예: "6" 또는 "06"

    op.order_year = _parse_int(year_raw)

    if month_raw is not None and month_raw != "":
        month_str = str(month_raw).zfill(2)  # "6" -> "06"
        op.order_month = month_str

        if op.order_year is not None:
            op.order_ym = f"{op.order_year}{month_str}"  # "2025" + "12" -> "202512"
        else:
            op.order_ym = None
    else:
        op.order_month = None
        op.order_ym = None

    # 🔹 나머지 필드들
    op.order_instt_cd = item.get("orderInsttCd")
    op.order_instt_nm = item.get("orderInsttNm")
    op.biz_nm = item.get("bizNm")
    op.sum_order_amt = _parse_numeric(item.get("sumOrderAmt"))
    op.ntce_ntice_yn = item.get("ntceNticeYn")
    op.ntce_dt = _parse_dt(item.get("nticeDt"))
    op.bid_ntce_no_list = item.get("bidNtceNoList")
    op.source_api = source_api
    op.raw_json = item  # 전체 item 저장

async def sync_order_plan_recent():
    """
    발주시기 기준:
      - 기준월(현재월) ~ 기준월 + 3개월

    게시일시 기준:
      - 매우 넓은 기간 (2000-01-01 ~ 2099-12-31)
        → 나라장터 기본값(최근 1일) 방지

    범위의 발주계획을 나라장터에서 가져와 order_plan 테이블에 upsert한다.
    """

    now = datetime.now()

    # ✅ 기준월: 현재월의 1일 00:00 기준
    base_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # ✅ 발주시기: 기준월 ~ 기준월 + 3개월
    order_bgn_ym = base_month.strftime("%Y%m")                         # ex) "202512"
    order_end_ym = (base_month + relativedelta(months=3)).strftime("%Y%m")

    # ✅ 게시일시 조회 기간: 넉넉하게 전체 구간
    inqry_bgn_dt = "200001010000"   # 2000-01-01 00:00
    inqry_end_dt = "209912312359"   # 2099-12-31 23:59

    num_of_rows = 100
    page = 1

    with SessionLocal() as db:
        while True:
            raw = await fetch_order_plan_search_page(
                page=page,
                num_of_rows=num_of_rows,
                inqry_bgn_dt=inqry_bgn_dt,
                inqry_end_dt=inqry_end_dt,
                order_bgn_ym=order_bgn_ym,
                order_end_ym=order_end_ym,
            )

            items = extract_order_plan_items_from_search(raw)
            paging = extract_paging_from_search(raw)

            if not items:
                break

            total_count = paging.get("totalCount", 0)
            total_pages = math.ceil(total_count / num_of_rows) if num_of_rows > 0 else 1

            print(
                f"[SYNC][ORDER_PLAN] page {page}/{total_pages} - "
                f"fetched {len(items)} items (totalCount={total_count}, "
                f"order_bgn_ym={order_bgn_ym}, order_end_ym={order_end_ym}, "
                f"inqry_bgn_dt={inqry_bgn_dt}, inqry_end_dt={inqry_end_dt})"
            )

            for item in items:
                upsert_order_plan(db, item)

            db.commit()

            if page >= total_pages:
                break

            page += 1

# app/services/order_plan_sync.py 맨 아래에 추가

from datetime import datetime
from app.db.session import SessionLocal  # 이미 위에 있으면 중복 import 제거해도 됨


async def sync_order_plan_december_sample() -> None:
    """
    테스트용:
    - 올해 12월 발주시기(orderBgnYm=YYYY12, orderEndYm=YYYY12)만
    - 한 페이지(최대 100건)만 가져와서 order_plan 테이블에 저장
    """

    now = datetime.now()
    year = now.year
    ym = "202601"  # 예: 202512

    num_of_rows = 100
    page = 1

    print(
        f"[SYNC-DEC] fetching sample for orderYm={ym}, "
        f"page={page}, num_of_rows={num_of_rows}"
    )

    # 🔹 조달청 발주계획 '검색' 오퍼레이션 호출
    raw = await fetch_order_plan_search_page(
        page=page,
        num_of_rows=num_of_rows,
        order_bgn_ym=ym,
        order_end_ym=ym,

    )

    items = extract_order_plan_items_from_search(raw)
    paging = extract_paging_from_search(raw)

    print(
        f"[SYNC-DEC] fetched {len(items)} items for {ym} "
        f"(pageNo={paging.get('pageNo')}, totalCount={paging.get('totalCount')})"
    )

    # 🔹 DB에 upsert
    with SessionLocal() as db:
        for item in items:
            upsert_order_plan(db, item, source_api="december_sample")
        db.commit()

    print(f"[SYNC-DEC] committed {len(items)} items for {ym} to DB.")
