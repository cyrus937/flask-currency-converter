# # app/routes/auth.py
import http
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.auth_service import AuthService
from app.schemas.auth_schemas import (
    RegisterSchema, LoginSchema, RefreshTokenSchema, 
    ChangePasswordSchema
)
from app.schemas.response_schemas import (
    MessageSchema, LoginResponseSchema, RefreshResponseSchema,
    ErrorSchema, SessionsResponseSchema
)
from app.schemas.user_schemas import UserProfileSchema
from app.middleware.rate_limiter import limiter
from app.utils.exceptions import AuthenticationError, ValidationError as CustomValidationError
import logging

auth_bp = Blueprint(
    'auth', 
    __name__, 
    url_prefix='/api/auth',
    description='Authentification et gestion des comptes utilisateur'
)


@auth_bp.route('/register', methods=['POST'])
@auth_bp.doc(
    summary="Enregistrement d'un nouvel utilisateur",
    description="Crée un nouveau compte utilisateur avec email et mot de passe.",
    tags=['Authentication'],)
@auth_bp.arguments(RegisterSchema, location='json', content_type='application/json')
@auth_bp.response(201, UserProfileSchema, content_type='application/json')
@auth_bp.alt_response(400, schema=ErrorSchema, description='Erreur de validation', content_type='application/json')
@limiter.limit("5 per minute")
def register(args):
    """
    Enregistrement d'un nouvel utilisateur
    
    Crée un nouveau compte utilisateur avec email et mot de passe.
    L'email doit être unique et le mot de passe doit respecter les critères de sécurité.
    """
    try:
        data = request.get_json(silent=True)
        user = AuthService.register_user(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            preferred_currency=data.get('preferred_currency', 'USD')
        ).to_dict(include_sensitive=True)
        
        return user
        
    except (AuthenticationError, CustomValidationError) as e:
        abort(400, message=e.message, errors=e.__dict__)
    except Exception as e :
        abort(500, message='Erreur lors de la création du compte', errors = {"error": str(e)})


@auth_bp.route('/login', methods=['POST'])
@auth_bp.doc(
    summary="Connexion utilisateur",
    description="Authentifie un utilisateur et retourne les tokens JWT.",
    tags=['Authentication'],)
@auth_bp.arguments(LoginSchema, location='json')
@auth_bp.response(200, LoginResponseSchema, content_type='application/json')
@auth_bp.alt_response(400, http.HTTPStatus(400).name, schema=ErrorSchema, description="Échec d'authentification")
@auth_bp.alt_response(500, http.HTTPStatus(500).name, schema=ErrorSchema, description="Erreur interne")
@limiter.limit("10 per minute")
def login(args):
    """
    Connexion utilisateur
    
    Authentifie un utilisateur et retourne les tokens JWT.
    Crée une nouvelle session de connexion.
    """
    try:
        args = request.get_json()
        result = AuthService.authenticate_user(
            email=args['email'],
            password=args['password'],
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return {
            'message': 'Connexion réussie',
            'user': result['user'].to_dict(include_sensitive=True),
            'access_token': result['access_token'],
            'refresh_token': result['refresh_token'],
            'session_id': result['session'].id
        }
        
    except AuthenticationError as e:
        abort(400, errors=e.__dict__, message = e.message)
    except Exception as ex:
        abort(500, errors={
            "error": "ServerError",
            "code": 500,
            "details": str(ex)
        }, message = str(ex))


@auth_bp.route('/refresh', methods=['POST'])
@auth_bp.arguments(RefreshTokenSchema, location='json')
@auth_bp.doc(
    summary="Rafraîchissement des tokens",
    description="Génère de nouveaux tokens JWT à partir d'un refresh token valide.",
    tags=['Authentication'],)
@auth_bp.response(200, RefreshResponseSchema)
@auth_bp.alt_response(400, schema=ErrorSchema)
@limiter.limit("20 per minute")
def refresh(args):
    """
    Rafraîchissement des tokens
    
    Génère de nouveaux tokens JWT à partir d'un refresh token valide.
    L'ancien refresh token est automatiquement révoqué.
    """
    try:
        from flask_jwt_extended import decode_token
        
        decoded_token = decode_token(args['refresh_token'])
        user_id = decoded_token['sub']
        jti = decoded_token['jti']
        
        result = AuthService.refresh_tokens(jti, user_id)
        
        return {
            'message': 'Tokens rafraîchis',
            'access_token': result['access_token'],
            'refresh_token': result['refresh_token']
        }
        
    except AuthenticationError as e:
        abort(400, message=str(e), errors=e.__dict__)
    except Exception as ex:
        abort(500, message='Erreur lors du rafraîchissement')


@auth_bp.route('/logout', methods=['POST'])
@auth_bp.doc(
    summary="Déconnexion utilisateur",
    description="Déconnecte l'utilisateur de la session actuelle.",
    tags=['Authentication'],
    security=[{"bearerAuth": []}])
@auth_bp.response(200, MessageSchema)
@auth_bp.alt_response(401, schema=ErrorSchema)
@jwt_required()
def logout():
    """
    Déconnexion utilisateur
    
    Déconnecte l'utilisateur de la session actuelle.
    Révoque les tokens associés à cette session.
    """
    try:
        # TODO: Lorsqu'on se déconnecte, on révoque le token d'accès et le refresh token sur la session actuelle. On ne doit plus pouvoir se reconnecter avec un ancien token.
        user_id = get_jwt_identity()
        claims = get_jwt()
        session_id = claims.get('session_id')
        
        AuthService.logout_user(user_id, session_id)
        
        return {'message': 'Déconnexion réussie'}
        
    except Exception:
        abort(500, message='Erreur lors de la déconnexion')


@auth_bp.route('/logout-all', methods=['POST'])
@auth_bp.doc(
    summary="Déconnexion de toutes les sessions",
    description="Déconnecte l'utilisateur de toutes ses sessions actives.",
    tags=['Authentication'],
    security=[{"bearerAuth": []}])
@auth_bp.response(200, MessageSchema)
@jwt_required()
def logout_all():
    """
    Déconnexion de toutes les sessions
    
    Déconnecte l'utilisateur de toutes ses sessions actives.
    Révoque tous les tokens associés au compte.
    """
    try:
        # TODO: Lorsqu'on se déconnecte de toutes les sessions, on révoque tous les tokens d'accès et refresh tokens. On ne doit plus pouvoir se reconnecter avec un ancien token.
        user_id = get_jwt_identity()
        AuthService.logout_user(user_id)
        
        return {'message': 'Déconnexion de toutes les sessions réussie'}
        
    except Exception:
        abort(500, message='Erreur lors de la déconnexion')


@auth_bp.route('/change-password', methods=['POST'])
@auth_bp.doc(
    summary="Changement de mot de passe",
    description="Modifie le mot de passe de l'utilisateur connecté.",
    tags=['Authentication'],
    security=[{"bearerAuth": []}])
@auth_bp.arguments(ChangePasswordSchema, location='json')
@auth_bp.response(200, MessageSchema)
@auth_bp.alt_response(400, schema=ErrorSchema)
@jwt_required()
@limiter.limit("3 per minute")
def change_password(args):
    """
    Changement de mot de passe
    
    Modifie le mot de passe de l'utilisateur connecté.
    Nécessite le mot de passe actuel pour validation.
    """
    try:
        user_id = get_jwt_identity()
        AuthService.change_password(
            user_id=user_id,
            current_password=args['current_password'],
            new_password=args['new_password']
        )
        
        return {'message': 'Mot de passe modifié avec succès'}
        
    except (AuthenticationError, CustomValidationError) as e:
        abort(400, message=str(e))
    except Exception:
        abort(500, message='Erreur lors du changement de mot de passe')


@auth_bp.route('/profile', methods=['GET'])
@auth_bp.doc(
    summary="Profil utilisateur détaillé",
    description="Récupère toutes les informations du profil utilisateur avec statistiques",
    tags=['Authentication'],
    security=[{"bearerAuth": []}])
@auth_bp.response(200, UserProfileSchema)
@auth_bp.alt_response(404, schema=ErrorSchema)
@jwt_required()
def get_profile():
    """
    Récupération du profil utilisateur
    
    Retourne les informations détaillées du profil de l'utilisateur connecté.
    Inclut les devises favorites et statistiques de session.
    """
    try:
        from app.models.user import User
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            abort(404, message='Utilisateur non trouvé')
        
        return user.to_dict(include_sensitive=True)
        
    except Exception:
        abort(500, message='Erreur lors de la récupération du profil')


@auth_bp.route('/sessions', methods=['GET'])
@auth_bp.doc(
    summary="Liste des sessions actives",
    description="Retourne toutes les sessions actives de l'utilisateur.",
    tags=['Authentication'],
    security=[{"bearerAuth": []}])
@auth_bp.response(200, SessionsResponseSchema)
@jwt_required()
def get_sessions():
    """
    Liste des sessions actives
    
    Retourne toutes les sessions actives de l'utilisateur.
    Permet d'identifier les appareils connectés.
    """
    try:
        from app.services.session_service import SessionService
        
        user_id = get_jwt_identity()
        sessions = SessionService.get_user_sessions(user_id, active_only=True)
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'id': session.id,
                'device_type': session.device_type,
                'ip_address': session.ip_address,
                'user_agent': session.user_agent,
                'created_at': session.created_at,
                'last_activity': session.last_activity,
                'is_current': session.id == get_jwt().get('session_id')
            })
        
        return {'sessions': sessions_data}
        
    except Exception:
        abort(500, message='Erreur lors de la récupération des sessions')


@auth_bp.route('/sessions/<session_id>', methods=['DELETE'])
@auth_bp.doc(
    summary="Suppression d'une session spécifique",
    description="Déconnecte un appareil spécifique en supprimant sa session.",
    tags=['Authentication'],
    security=[{"bearerAuth": []}])
@auth_bp.response(200, MessageSchema)
@auth_bp.alt_response(404, schema=ErrorSchema)
@jwt_required()
def delete_session(session_id):
    """
    Suppression d'une session spécifique
    
    Déconnecte un appareil spécifique en supprimant sa session.
    Utile pour déconnecter des appareils perdus ou volés.
    """
    try:
        from app.services.session_service import SessionService
        from app.models.session import Session
        
        user_id = get_jwt_identity()
        
        session = Session.query.filter_by(id=session_id, user_id=user_id).first()
        if not session:
            abort(404, message='Session non trouvée')
        
        SessionService.deactivate_session(session_id)
        
        return {'message': 'Session supprimée'}
        
    except Exception:
        abort(500, message='Erreur lors de la suppression de la session')