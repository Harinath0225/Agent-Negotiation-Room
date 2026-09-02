from sqlalchemy import Column, String, Integer, Boolean, JSON
from .db import Base
import uuid

class UISchema(Base):
    __tablename__ = "ui_schemas"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    version = Column(Integer, default=1)
    layout = Column(JSON, nullable=False)
    is_published = Column(Boolean, default=False)
