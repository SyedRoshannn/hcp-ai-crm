import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON
from app.db.base import Base

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hcp_name = Column(String(255), nullable=True)
    interaction_type = Column(String(50), nullable=True)
    date = Column(String(100), nullable=True)
    time = Column(String(50), nullable=True)
    attendees = Column(JSON, default=list, nullable=False)
    topics_discussed = Column(JSON, default=list, nullable=False)
    materials_shared = Column(JSON, default=list, nullable=False)
    samples_distributed = Column(JSON, default=list, nullable=False)
    sentiment = Column(String(50), nullable=True)
    outcomes = Column(Text, nullable=True)
    follow_up_actions = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
