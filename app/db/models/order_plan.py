# app/db/models/order_plan.py
from sqlalchemy import (
    BigInteger,
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    JSON,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.session import Base


class OrderPlan(Base):
    __tablename__ = "order_plan"

    id = Column(BigInteger, primary_key=True, index=True)

    order_plan_unty_no = Column(String(30), nullable=False, unique=True)
    order_year = Column(Integer)
    order_instt_cd = Column(String(10))
    order_instt_nm = Column(String(200))

    # 🔹 여기 추가
    order_month = Column(String(2))   # "01" ~ "12"
    order_ym = Column(String(6))      # "YYYYMM"

    biz_nm = Column(String(400))
    sum_order_amt = Column(Numeric(18, 0))
    ntce_ntice_yn = Column(String(1))
    ntice_dt = Column(DateTime)

    bid_ntce_no_list = Column(String(1000))

    source_api = Column(String(50))
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())

    raw_json = Column(JSONB)  # PostgreSQL jsonb
