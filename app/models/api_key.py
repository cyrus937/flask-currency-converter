from app.models.base import BaseModel
from app.extensions import db
import secrets
import hashlib

class ApiKey(BaseModel):
    """Modèle représentant une clé API"""
    __tablename__ = 'api_keys'
    
    name = db.Column(db.String(150), nullable=False)  # Nom de l’app externe
    key_hash = db.Column(db.String(64), unique=True, nullable=False)  # SHA256
    active = db.Column(db.Boolean, default=True)
    owner_id = db.Column(db.String(36), db.ForeignKey("users.id"))  # Si lié à un utilisateur
    
    @classmethod
    def find_by_key(cls, key):
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return cls.query.filter_by(key_hash=key_hash, active=True).first()

    @classmethod
    def create_api_key(cls, name, owner_id):
        key, key_hash = cls.generate_api_key()
        api_key = cls(
            name=name,
            key_hash=key_hash,
            owner_id=owner_id
        )
        api_key.save()
        return api_key, key

    @classmethod
    def generate_api_key():
        # Génération d’une clé aléatoire sécurisée
        key = secrets.token_urlsafe(32)  # clé à donner au client
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return key, key_hash
    
    @classmethod
    def get_all_active_keys(cls):
        """Récupère toutes les clés API actives"""
        return cls.query.filter_by(active=True).all()
    
    @classmethod
    def deactivate_key(cls, key_id):
        """Désactive une clé API
        
        Parameters
            key_id (str): L'ID de la clé API à désactiver
        """
        api_key = cls.query.get(key_id)
        if api_key:
            api_key.active = False
            api_key.save()

    def deactivate(self):
        """Désactive la clé API"""
        self.active = False
        self.save()