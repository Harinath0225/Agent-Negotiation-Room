from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..models.db import get_db
from ..models.schema import DealRecord

router = APIRouter(prefix="/contracts", tags=["contracts"])


class CreateDealInput(BaseModel):
    company: str = Field(..., description="Counterparty company name (e.g. Acme Corp)")
    value: int = Field(..., ge=0, description="Annual deal value in USD (e.g. 2000000)")
    stage: str = Field(default="Draft", description="Deal stage: Draft, Negotiation, Approved, Closed Won, Rejected")
    title: Optional[str] = Field(default=None, description="Deal title / project description")
    liability_cap: Optional[str] = Field(default="1.5x", description="Liability cap multiplier")


class UpdateStageInput(BaseModel):
    stage: str = Field(..., description="Target stage: Draft, Negotiation, Approved, Closed Won, Rejected")


class AddNoteInput(BaseModel):
    note: str = Field(..., min_length=1, description="Negotiation or context note text")
    author: Optional[str] = Field(default="ChatGPT Agent", description="Author of the note")


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
        records = records.filter(DealRecord.status.ilike(status))
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
                "notes_count": len(record.notes or []),
                "updated_at": record.updated_at,
            }
            for record in matches
        ],
    }


@router.post("", status_code=201)
def create_deal(payload: CreateDealInput, db: Session = Depends(get_db)):
    """Create a new deal in the system (callable by WebMCP agents e.g. ChatGPT)."""
    now = datetime.now(timezone.utc).isoformat()
    contract_num = uuid.uuid4().hex[:4].upper()
    contract_id = f"{contract_num}-D"
    title = payload.title or f"{payload.company} Enterprise Service Agreement"

    deal = DealRecord(
        id=f"deal_{uuid.uuid4().hex[:8]}",
        contract_id=contract_id,
        title=title,
        counterparty=payload.company,
        status=payload.stage,
        annual_value=payload.value,
        liability_cap=payload.liability_cap or "1.5x",
        notes=[{
            "id": f"note_{uuid.uuid4().hex[:6]}",
            "author": "WebMCP Agent",
            "note": f"Initial deal created with status '{payload.stage}' and value ${payload.value:,}.",
            "timestamp": now
        }],
        updated_at=now,
    )
    db.add(deal)
    db.commit()
    db.refresh(deal)

    return {
        "success": True,
        "message": f"Deal '{deal.title}' successfully created with ID #{deal.contract_id}.",
        "deal": {
            "id": deal.id,
            "contract_id": deal.contract_id,
            "title": deal.title,
            "counterparty": deal.counterparty,
            "status": deal.status,
            "annual_value": deal.annual_value,
            "liability_cap": deal.liability_cap,
            "notes": deal.notes,
            "updated_at": deal.updated_at,
        }
    }


@router.get("/{contract_id}")
def get_deal(contract_id: str, db: Session = Depends(get_db)):
    """Retrieve details and notes for a specific contract."""
    clean_id = contract_id.strip().lstrip("#")
    deal = db.query(DealRecord).filter(
        or_(
            DealRecord.contract_id == clean_id,
            DealRecord.contract_id == contract_id,
            DealRecord.id == contract_id
        )
    ).first()

    if not deal:
        raise HTTPException(status_code=404, detail=f"Contract #{contract_id} not found.")

    return {
        "id": deal.id,
        "contract_id": deal.contract_id,
        "title": deal.title,
        "counterparty": deal.counterparty,
        "status": deal.status,
        "annual_value": deal.annual_value,
        "liability_cap": deal.liability_cap,
        "notes": deal.notes or [],
        "updated_at": deal.updated_at,
    }


@router.patch("/{contract_id}/stage")
def move_deal_stage(contract_id: str, payload: UpdateStageInput, db: Session = Depends(get_db)):
    """Move a deal to a new stage (e.g. Negotiation, Closed Won)."""
    clean_id = contract_id.strip().lstrip("#")
    deal = db.query(DealRecord).filter(
        or_(
            DealRecord.contract_id == clean_id,
            DealRecord.contract_id == contract_id,
            DealRecord.id == contract_id
        )
    ).first()

    if not deal:
        raise HTTPException(status_code=404, detail=f"Contract #{contract_id} not found.")

    old_status = deal.status
    deal.status = payload.stage
    deal.updated_at = datetime.now(timezone.utc).isoformat()
    
    current_notes = list(deal.notes or [])
    current_notes.append({
        "id": f"note_{uuid.uuid4().hex[:6]}",
        "author": "WebMCP Workflow",
        "note": f"Stage transitioned from '{old_status}' to '{payload.stage}'.",
        "timestamp": deal.updated_at
    })
    deal.notes = current_notes

    db.commit()
    db.refresh(deal)

    return {
        "success": True,
        "contract_id": deal.contract_id,
        "old_status": old_status,
        "new_status": deal.status,
        "message": f"Deal #{deal.contract_id} successfully moved to stage '{deal.status}'."
    }


@router.post("/{contract_id}/notes")
def add_deal_note(contract_id: str, payload: AddNoteInput, db: Session = Depends(get_db)):
    """Add a structured note to a contract record."""
    clean_id = contract_id.strip().lstrip("#")
    deal = db.query(DealRecord).filter(
        or_(
            DealRecord.contract_id == clean_id,
            DealRecord.contract_id == contract_id,
            DealRecord.id == contract_id
        )
    ).first()

    if not deal:
        raise HTTPException(status_code=404, detail=f"Contract #{contract_id} not found.")

    now = datetime.now(timezone.utc).isoformat()
    note_obj = {
        "id": f"note_{uuid.uuid4().hex[:6]}",
        "author": payload.author or "ChatGPT Agent",
        "note": payload.note,
        "timestamp": now
    }
    
    current_notes = list(deal.notes or [])
    current_notes.append(note_obj)
    deal.notes = current_notes
    deal.updated_at = now

    db.commit()
    db.refresh(deal)

    return {
        "success": True,
        "contract_id": deal.contract_id,
        "note": note_obj,
        "total_notes": len(deal.notes)
    }


@router.delete("/{contract_id}")
def delete_deal(contract_id: str, db: Session = Depends(get_db)):
    """Delete a contract record."""
    clean_id = contract_id.strip().lstrip("#")
    deal = db.query(DealRecord).filter(
        or_(
            DealRecord.contract_id == clean_id,
            DealRecord.contract_id == contract_id,
            DealRecord.id == contract_id
        )
    ).first()

    if not deal:
        raise HTTPException(status_code=404, detail=f"Contract #{contract_id} not found.")

    db.delete(deal)
    db.commit()
    return {"success": True, "message": f"Contract #{contract_id} deleted."}