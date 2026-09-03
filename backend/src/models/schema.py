from sqlalchemy import Column, String, Integer, Boolean, JSON
from .db import Base
import uuid

class UISchema(Base):
    __tablename__ = "ui_schemas"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    version = Column(Integer, default=1)
    layout = Column(JSON, nullable=False)
    is_published = Column(Boolean, default=False)


class DealRecord(Base):
    __tablename__ = "deal_records"

    id = Column(String, primary_key=True)
    contract_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    counterparty = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, index=True)
    annual_value = Column(Integer, nullable=False)
    liability_cap = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)
    notes = Column(JSON, default=list, nullable=True)
