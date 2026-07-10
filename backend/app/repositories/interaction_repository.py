from sqlalchemy import cast, String
from sqlalchemy.orm import Session
from app.models.interaction import Interaction
from typing import List, Optional

class InteractionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_interaction(self, interaction_data: dict) -> Interaction:
        db_interaction = Interaction(**interaction_data)
        self.db.add(db_interaction)
        self.db.commit()
        self.db.refresh(db_interaction)
        return db_interaction

    def get_by_id(self, interaction_id: str) -> Optional[Interaction]:
        return self.db.query(Interaction).filter(Interaction.id == interaction_id).first()

    def get_all(self) -> List[Interaction]:
        return self.db.query(Interaction).order_by(Interaction.created_at.desc()).all()

    def get_latest(self) -> Optional[Interaction]:
        return self.db.query(Interaction).order_by(Interaction.created_at.desc()).first()

    def get_by_doctor(self, doctor_name: str) -> List[Interaction]:
        return self.db.query(Interaction).filter(Interaction.hcp_name.ilike(f"%{doctor_name}%")).order_by(Interaction.created_at.desc()).all()

    def get_by_date(self, date: str) -> List[Interaction]:
        return self.db.query(Interaction).filter(Interaction.date.ilike(f"%{date}%")).order_by(Interaction.created_at.desc()).all()

    def get_by_sentiment(self, sentiment: str) -> List[Interaction]:
        return self.db.query(Interaction).filter(Interaction.sentiment.ilike(f"%{sentiment}%")).order_by(Interaction.created_at.desc()).all()

    def search(self, filters: dict) -> List[Interaction]:
        """Dynamic generic filter query runner supporting multi-parameter matching."""
        query = self.db.query(Interaction)
        
        # 1. Filter by doctor name (HCP name)
        doctor_name = filters.get("doctor_name")
        if doctor_name:
            query = query.filter(Interaction.hcp_name.ilike(f"%{doctor_name}%"))
            
        # 2. Filter by sentiment
        sentiment = filters.get("sentiment")
        if sentiment:
            query = query.filter(Interaction.sentiment.ilike(f"%{sentiment}%"))
            
        # 3. Filter by interaction type
        interaction_type = filters.get("interaction_type")
        if interaction_type:
            query = query.filter(Interaction.interaction_type.ilike(f"%{interaction_type}%"))
            
        # 4. Filter by date / date range
        date = filters.get("date")
        if date:
            query = query.filter(Interaction.date.ilike(f"%{date}%"))
            
        # 5. Filter by material (shared)
        material = filters.get("material")
        if material:
            query = query.filter(cast(Interaction.materials_shared, String).ilike(f"%{material}%"))
            
        # 6. Filter by topic discussed
        topic = filters.get("topic")
        if topic:
            query = query.filter(cast(Interaction.topics_discussed, String).ilike(f"%{topic}%"))
            
        # 7. Filter by followup existence
        has_followup = filters.get("has_followup")
        if has_followup:
            query = query.filter(
                Interaction.follow_up_actions.isnot(None), 
                cast(Interaction.follow_up_actions, String) != '[]', 
                cast(Interaction.follow_up_actions, String) != ''
            )
            
        # 8. Sort by created_at desc (latest first)
        query = query.order_by(Interaction.created_at.desc())
        
        # 9. If latest is requested
        if filters.get("latest"):
            result = query.first()
            return [result] if result else []
            
        return query.all()

    def update(self, interaction_id: str, update_data: dict) -> Optional[Interaction]:
        db_interaction = self.get_by_id(interaction_id)
        if not db_interaction:
            return None
        for key, value in update_data.items():
            if hasattr(db_interaction, key):
                setattr(db_interaction, key, value)
        self.db.commit()
        self.db.refresh(db_interaction)
        return db_interaction

    def delete(self, interaction_id: str) -> bool:
        db_interaction = self.get_by_id(interaction_id)
        if not db_interaction:
            return False
        self.db.delete(db_interaction)
        self.db.commit()
        return True
