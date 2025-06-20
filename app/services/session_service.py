# app/services/session_service.py
from datetime import datetime
import secrets
from app.models.session import Session
from app.services.token_service import TokenService


class SessionService:
    """Service de gestion des sessions"""
    
    @staticmethod
    def create_session(user_id, ip_address=None, user_agent=None, device_type='web'):
        """Crée une nouvelle session"""
        
        session_token = secrets.token_urlsafe(32)
        
        session = Session(
            user_id=user_id,
            session_token=session_token,
            ip_address=ip_address,
            user_agent=user_agent,
            device_type=device_type
        )
        
        return session.save()
    
    @staticmethod
    def get_user_sessions(user_id, active_only=True):
        """Récupère les sessions d'un utilisateur"""
        query = Session.query.filter_by(user_id=user_id)
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        return query.order_by(Session.last_activity.desc()).all()
    
    @staticmethod
    def deactivate_session(session_id):
        """Désactive une session et révoque les tokens associés"""
        
        session = Session.query.get(session_id)
        if not session:
            return False
        
        # Désactiver la session
        session.deactivate()
        
        # Révoquer tous les refresh tokens de cette session
        for refresh_token in session.refresh_tokens:
            if not refresh_token.is_revoked:
                refresh_token.revoke()
                
                # Ajouter le JTI à la blacklist
                TokenService.blacklist_token(refresh_token.jti, 3600)  # 1 heure
        
        return True
    
    @staticmethod
    def cleanup_expired_sessions():
        """Nettoie les sessions expirées"""
        return Session.cleanup_expired_sessions()
