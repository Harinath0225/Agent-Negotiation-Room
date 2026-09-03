from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..models.db import get_db
from ..models.schema import DealRecord

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.get("")
def search_contracts(
    query: Optional[str] = Query(default=None, max_length=100),
    status: Optional[str] = Query(default=None, max_length=30),
    min_value: Optional[int] = Query(default=None, ge=0),
    max_value: Optional[int] = Query(default=None, ge=0),
    db: Session = Depends(get_db),
):
    records = db.query(DealRecord)

    if query:
        escaped_query = f"%{query.strip()}%"
        records = records.filter(
            or_(
                DealRecord.contract_id.ilike(escaped_query),
                DealRecord.title.ilike(escaped_query),
                DealRecord.counterparty.ilike(escaped_query),
            )
        )
    if status:
        records = records.filter(DealRecord.status == status)
    if min_value is not None:
        records = records.filter(DealRecord.annual_value >= min_value)
    if max_value is not None:
        records = records.filter(DealRecord.annual_value <= max_value)

    matches = records.order_by(DealRecord.updated_at.desc()).all()
    return {
        "count": len(matches),
        "records": [
            {
                "id": record.id,
                "contract_id": record.contract_id,
                "title": record.title,
                "counterparty": record.counterparty,
                "status": record.status,
                "annual_value": record.annual_value,
                "liability_cap": record.liability_cap,
                "updated_at": record.updated_at,
            }
            for record in matches
        ],
    }