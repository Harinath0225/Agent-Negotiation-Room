from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.db import get_db
from ..models.schema import UISchema

router = APIRouter()

@router.get("/ui-schema")
def get_current_ui_schema(db: Session = Depends(get_db)):
    # In a real app, we might query by 'is_published=True'
    # For MVP, just get the first one or return a default seed if none exist
    schema = db.query(UISchema).filter(UISchema.is_published == True).first()
    
    if not schema:
        # Fallback to a default schema structure if DB is empty
        return {
            "id": "default",
            "version": 1,
            "is_published": True,
            "layout": {
                "type": "div",
                "className": "min-h-screen bg-slate-900 text-white p-8 flex flex-col items-center justify-center",
                "children": [
                    {
                        "type": "h1",
                        "className": "text-4xl font-bold mb-4",
                        "props": {"text": "Nexus Deal Room"}
                    },
                    {
                        "type": "p",
                        "className": "text-lg text-slate-300",
                        "props": {"text": "Awaiting layout from schema..."}
                    }
                ]
            }
        }
    
    return {
        "id": schema.id,
        "version": schema.version,
        "is_published": schema.is_published,
        "layout": schema.layout
    }
