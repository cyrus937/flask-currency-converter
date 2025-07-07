# app/services/auth_service.py
from flask import request
from werkzeug.security import generate_password_hash
from datetime import datetime
import secrets
from app.models.user import User
from app.models.session import Session
from app.models.refresh_token import RefreshToken
from app.services.session_service import SessionService
from app.services.token_service import TokenService
from app.utils.exceptions import AuthenticationError, ValidationError
import logging


class AuthService:
    """Service d'authentification"""
    
    @staticmethod
    def register_user(email, password, first_name, last_name, preferred_currency='USD'):
        """Enregistre un nouvel utilisateur"""
        
        # Validation basique
        if not email or not password or not first_name or not last_name:
            logging.error("Tous les champs sont requis pour l'enregistrement")
            raise ValidationError("Tous les champs sont requis", 400)
        
        if len(password) < 8:
            logging.error("Le mot de passe doit contenir au moins 8 caractères")
            raise ValidationError("Le mot de passe doit contenir au moins 8 caractères", 400)
        
        # Vérifier si l'utilisateur existe déjà
        if User.find_by_email(email):
            logging.error(f"Un utilisateur avec l'email {email} existe déjà")
            raise ValidationError("Un utilisateur avec cet email existe déjà", 400)
        
        # Créer l'utilisateur
        user = User.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        user.preferred_currency = preferred_currency
        user.save()

        return user
    
    @staticmethod
    def authenticate_user(email, password, ip_address=None, user_agent=None):
        """Authentifie un utilisateur et crée une session"""
        
        # Trouver l'utilisateur
        user: User = User.find_by_email(email)
        
        if not user or not user.check_password(password):
            print(f"Authentication failed for email: {email}")
            raise AuthenticationError("Email ou mot de passe incorrect", 400)
        
        if not user.is_active:
            print(f"Compte désactivé pour l'utilisateur: {email}")
            raise AuthenticationError("Compte désactivé", 400)
        
        # Vérifier le nombre de sessions
        if not user.can_create_session():
            print(f"Nombre maximum de sessions atteint pour l'utilisateur: {email}")
            raise AuthenticationError("Nombre maximum de sessions atteint", 400)
        
        # Créer une session
        session = SessionService.create_session(
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Générer les tokens
        access_token, refresh_token = user.generate_tokens(session.id)
        
        # Sauvegarder le refresh token
        refresh_token_obj = RefreshToken(
            user_id=user.id,
            session_id=session.id,
            jti=TokenService.get_jti_from_token(refresh_token)
        )
        refresh_token_obj.save()
        
        # Mettre à jour la dernière connexion
        user.update_last_login()
        
        return {
            'user': user,
            'session': session,
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    
    @staticmethod
    def logout_user(user_id, session_id=None):
        """Déconnecte un utilisateur"""
        
        if session_id:
            # Déconnexion d'une session spécifique
            session = Session.query.filter_by(
                id=session_id,
                user_id=user_id,
                is_active=True
            ).first()
            
            if session:
                SessionService.deactivate_session(session.id)
        else:
            # Déconnexion de toutes les sessions
            sessions = Session.query.filter_by(
                user_id=user_id,
                is_active=True
            ).all()
            
            for session in sessions:
                SessionService.deactivate_session(session.id)
    
    @staticmethod
    def refresh_tokens(refresh_token_jti, user_id):
        """Rafraîchit les tokens d'accès"""
        
        # Vérifier le refresh token
        refresh_token_obj = RefreshToken.find_by_jti(refresh_token_jti)
        if not refresh_token_obj or not refresh_token_obj.is_valid():
            raise AuthenticationError("Refresh token invalide ou expiré")
        
        if refresh_token_obj.user_id != user_id:
            raise AuthenticationError("Token non autorisé pour cet utilisateur")
        
        # Récupérer l'utilisateur et la session
        user = User.query.get(user_id)
        session = Session.query.get(refresh_token_obj.session_id)
        
        if not user or not session or not session.is_active:
            raise AuthenticationError("Session invalide")
        
        # Révoquer l'ancien refresh token
        refresh_token_obj.revoke()
        
        # Générer de nouveaux tokens
        access_token, new_refresh_token = user.generate_tokens(session.id)
        
        # Sauvegarder le nouveau refresh token
        new_refresh_token_obj = RefreshToken(
            user_id=user.id,
            session_id=session.id,
            jti=TokenService.get_jti_from_token(new_refresh_token)
        )
        new_refresh_token_obj.save()
        
        # Mettre à jour l'activité de la session
        session.refresh_activity()
        
        return {
            'access_token': access_token,
            'refresh_token': new_refresh_token
        }
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """Change le mot de passe d'un utilisateur"""
        
        user = User.query.get(user_id)
        if not user:
            raise AuthenticationError("Utilisateur non trouvé")
        
        if not user.check_password(current_password):
            raise AuthenticationError("Mot de passe actuel incorrect")
        
        if len(new_password) < 8:
            raise ValidationError("Le nouveau mot de passe doit contenir au moins 8 caractères")
        
        # Changer le mot de passe
        user.set_password(new_password)
        user.save()
        
        # Déconnecter toutes les autres sessions pour sécurité
        AuthService.logout_user(user_id)
        
        return True
