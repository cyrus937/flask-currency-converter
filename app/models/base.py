# app/models/base.py
from datetime import datetime
from app.extensions import db
import uuid


class BaseModel(db.Model):
    """Modèle de base avec champs communs"""
    __abstract__ = True
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def save(self):
        """Sauvegarde l'objet en base"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Supprime l'objet de la base"""
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
