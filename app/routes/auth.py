# # app/routes/auth.py
# from flask import Blueprint, request, jsonify
# from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
# from marshmallow import ValidationError
# from app.services.auth_service import AuthService
# from app.schemas.auth_schemas import (
#     RegisterSchema, LoginSchema, RefreshTokenSchema, 
#     ChangePasswordSchema
# )
# from app.middleware.rate_limiter import limiter
# from app.utils.exceptions import AuthenticationError, ValidationError as CustomValidationError
# 
# auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
# 
# 
# @auth_bp.route('/register', methods=['POST'])
# @limiter.limit("5 per minute")
# def register():
#     """
#     Enregistrement d'un nouvel utilisateur
#     ---
#     POST /api/auth/register
#     {
#         "email": "user@example.com",
#         "password": "password123",
#         "first_name": "John",
#         "last_name": "Doe",
#         "preferred_currency": "USD"
#     }
#     """
#     schema = RegisterSchema()
#     
#     try:
#         data = schema.load(request.json)
#     except ValidationError as err:
#         return jsonify({'errors': err.messages}), 400
#     
#     try:
#         user = AuthService.register_user(
#             email=data['email'],
#             password=data['password'],
#             first_name=data['first_name'],
#             last_name=data['last_name'],
#             preferred_currency=data.get('preferred_currency', 'USD')
#         )
#         
#         return jsonify({
#             'message': 'Utilisateur créé avec succès',
#             'user': user.to_dict()
#         }), 201
#         
#     except (AuthenticationError, CustomValidationError) as e:
#         return jsonify({'error': str(e)}), 400
#     except Exception as e:
#         return jsonify({'error': 'Erreur lors de la création du compte'}), 500
# 
# 
# @auth_bp.route('/login', methods=['POST'])
# @limiter.limit("10 per minute")
# def login():
#     """
#     Connexion utilisateur
#     ---
#     POST /api/auth/login
#     {
#         "email": "user@example.com",
#         "password": "password123"
#     }
#     """
#     schema = LoginSchema()
#     
#     try:
#         data = schema.load(request.json)
#     except ValidationError as err:
#         return jsonify({'errors': err.messages}), 400
#     
#     try:
#         result = AuthService.authenticate_user(
#             email=data['email'],
#             password=data['password'],
#             ip_address=request.remote_addr,
#             user_agent=request.headers.get('User-Agent')
#         )
#         
#         return jsonify({
#             'message': 'Connexion réussie',
#             'user': result['user'].to_dict(),
#             'access_token': result['access_token'],
#             'refresh_token': result['refresh_token'],
#             'session_id': result['session'].id
#         }), 200
#         
#     except AuthenticationError as e:
#         return jsonify({'error': str(e)}), 401
#     except Exception as e:
#         return jsonify({'error': 'Erreur lors de la connexion'}), 500
# 
# 
# @auth_bp.route('/refresh', methods=['POST'])
# @limiter.limit("20 per minute")
# def refresh():
#     """
#     Rafraîchissement des tokens
#     ---
#     POST /api/auth/refresh
#     {
#         "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
#     }
#     """
#     schema = RefreshTokenSchema()
#     
#     try:
#         data = schema.load(request.json)
#     except ValidationError as err:
#         return jsonify({'errors': err.messages}), 400
#     
#     try:
#         from flask_jwt_extended import decode_token
#         
#         # Décoder le refresh token pour extraire les infos
#         decoded_token = decode_token(data['refresh_token'])
#         user_id = decoded_token['sub']
#         jti = decoded_token['jti']
#         
#         result = AuthService.refresh_tokens(jti, user_id)
#         
#         return jsonify({
#             'message': 'Tokens rafraîchis',
#             'access_token': result['access_token'],
#             'refresh_token': result['refresh_token']
#         }), 200
#         
#     except AuthenticationError as e:
#         return jsonify({'error': str(e)}), 401
#     except Exception as e:
#         return jsonify({'error': 'Erreur lors du rafraîchissement'}), 500
# 
# 
# @auth_bp.route('/logout', methods=['POST'])
# @jwt_required()
# def logout():
#     """
#     Déconnexion utilisateur
#     ---
#     POST /api/auth/logout
#     Headers: Authorization: Bearer <access_token>
#     """
#     try:
#         user_id = get_jwt_identity()
#         claims = get_jwt()
#         session_id = claims.get('session_id')
#         
#         AuthService.logout_user(user_id, session_id)
#         
#         return jsonify({'message': 'Déconnexion réussie'}), 200
#         
#     except Exception as e:
#         return jsonify({'error': 'Erreur lors de la déconnexion'}), 500
# 
# 
# @auth_bp.route('/logout-all', methods=['POST'])
# @jwt_required()
# def logout_all():
#     """
#     Déconnexion de toutes les sessions
#     ---
#     POST /api/auth/logout-all
#     Headers: Authorization: Bearer <access_token>
#     """
#     try:
#         user_id = get_jwt_identity()
#         AuthService.logout_user(user_id)  # Sans session_id = toutes les sessions
#         
#         return jsonify({'message': 'Déconnexion de toutes les sessions réussie'}), 200
#         
#     except Exception as e:
#         return jsonify({'error': 'Erreur lors de la déconnexion'}), 500
# 
# 
# @auth_bp.route('/change-password', methods=['POST'])
# @jwt_required()
# @limiter.limit("3 per minute")
# def change_password():
#     """
#     Changement de mot de passe
#     ---
#     POST /api/auth/change-password
#     {
#         "current_password": "oldpassword",
#         "new_password": "newpassword"
#     }
#     """
#     schema = ChangePasswordSchema()
#     
#     try:
#         data = schema.load(request.json)
#     except ValidationError as err:
#         return jsonify({'errors': err.messages}), 400
#     
#     try:
#         user_id = get_jwt_identity()
#         
#         AuthService.change_password(
#             user_id=user_id,
#             current_password=data['current_password'],
#             new_password=data['new_password']
#         )
#         
#         return jsonify({'message': 'Mot de passe modifié avec succès'}), 200
#         
#     except (AuthenticationError, CustomValidationError) as e:
#         return jsonify({'error': str(e)}), 400
#     except Exception as e:
#         return jsonify({'error': 'Erreur lors du changement de mot de passe'}), 500
# 
# 
# @auth_bp.route('/profile', methods=['GET'])
# @jwt_required()
# def get_profile():
#     """
#     Récupération du profil utilisateur
#     ---
#     GET /api/auth/profile
#     Headers: Authorization: Bearer <access_token>
#     """
#     try:
#         from app.models.user import User
#         
#         user_id = get_jwt_identity()
#         user = User.query.get(user_id)
#         
#         if not user:
#             return jsonify({'error': 'Utilisateur non trouvé'}), 404
#         
#         return jsonify({
#             'user': user.to_dict(include_sensitive=True)
#         }), 200
#         
#     except Exception as e:
#         return jsonify({'error': 'Erreur lors de la récupération du profil'}), 500
# 
# 
# @auth_bp.route('/sessions', methods=['GET'])
# @jwt_required()
# def get_sessions():
#     """
#     Liste des sessions actives
#     ---
#     GET /api/auth/sessions
#     Headers: Authorization: Bearer <access_token>
#     """
#     try:
#         from app.services.session_service import SessionService
#         
#         user_id = get_jwt_identity()
#         sessions = SessionService.get_user_sessions(user_id, active_only=True)
#         
#         sessions_data = []
#         for session in sessions:
#             sessions_data.append({
#                 'id': session.id,
#                 'device_type': session.device_type,
#                 'ip_address': session.ip_address,
#                 'user_agent': session.user_agent,
#                 'created_at': session.created_at.isoformat(),
#                 'last_activity': session.last_activity.isoformat(),
#                 'is_current': session.id == get_jwt().get('session_id')
#             })
#         
#         return jsonify({'sessions': sessions_data}), 200
#         
#     except Exception as e:
#         return jsonify({'error': 'Erreur lors de la récupération des sessions'}), 500
# 
# 
# @auth_bp.route('/sessions/<session_id>', methods=['DELETE'])
# @jwt_required()
# def delete_session(session_id):
#     """
#     Suppression d'une session spécifique
#     ---
#     DELETE /api/auth/sessions/<session_id>
#     Headers: Authorization: Bearer <access_token>
#     """
#     try:
#         from app.services.session_service import SessionService
#         
#         user_id = get_jwt_identity()
#         
#         # Vérifier que la session appartient à l'utilisateur
#         from app.models.session import Session
#         session = Session.query.filter_by(id=session_id, user_id=user_id).first()
#         
#         if not session:
#             return jsonify({'error': 'Session non trouvée'}), 404
#         
#         SessionService.deactivate_session(session_id)
#         
#         return jsonify({'message': 'Session supprimée'}), 200
#         
#     except Exception as e:
#         return jsonify({'error': 'Erreur lors de la suppression de la session'}), 500
# 

from typing import Any, Union
from flask import request
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError
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
@auth_bp.response(201, Union[MessageSchema, Any], content_type='application/json')
@auth_bp.response(400, ErrorSchema, content_type='application/json')
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
        print(f"Enregistrement de l'utilisateur avec email: {data}")
        user = AuthService.register_user(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            preferred_currency=data.get('preferred_currency', 'USD')
        )

        print(f"Utilisateur enregistré avec succès : {user}")
        
        return {
            'message': 'Utilisateur créé avec succès',
            'user': user.to_dict()
        }
        
    # except (AuthenticationError, CustomValidationError) as e:
    #     logging.error(f"Erreur lors de l'enregistrement : {str(e)}")
    #     abort(400, message=str(e))
    except Exception as e :
        print(f"Erreur inattendue lors de l'enregistrement : {str(e)}")
        abort(500, message='Erreur lors de la création du compte')


@auth_bp.route('/login', methods=['POST'])
@auth_bp.doc(
    summary="Connexion utilisateur",
    description="Authentifie un utilisateur et retourne les tokens JWT.",
    tags=['Authentication'],)
@auth_bp.arguments(LoginSchema, location='json')
@auth_bp.response(200, LoginResponseSchema)
@auth_bp.response(401, ErrorSchema)
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
            'user': result['user'].to_dict(),
            'access_token': result['access_token'],
            'refresh_token': result['refresh_token'],
            'session_id': result['session'].id
        }
        
    # except AuthenticationError as e:
    #     print(f"Erreur d'authentification : {str(e)}")
    #     abort(401, message=str(e))
    except Exception:
        abort(500, message='Erreur lors de la connexion')


@auth_bp.route('/refresh', methods=['POST'])
@auth_bp.arguments(RefreshTokenSchema, location='json')
@auth_bp.doc(
    summary="Rafraîchissement des tokens",
    description="Génère de nouveaux tokens JWT à partir d'un refresh token valide.",
    tags=['Authentication'],)
@auth_bp.response(200, RefreshResponseSchema)
@auth_bp.response(401, ErrorSchema)
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
        abort(401, message=str(e))
    except Exception:
        abort(500, message='Erreur lors du rafraîchissement')


@auth_bp.route('/logout', methods=['POST'])
@auth_bp.doc(
    summary="Déconnexion utilisateur",
    description="Déconnecte l'utilisateur de la session actuelle.",
    tags=['Authentication'],
    security=[{"bearerAuth": []}])
@auth_bp.response(200, MessageSchema)
@auth_bp.response(401, ErrorSchema)
@jwt_required()
def logout():
    """
    Déconnexion utilisateur
    
    Déconnecte l'utilisateur de la session actuelle.
    Révoque les tokens associés à cette session.
    """
    try:
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
@auth_bp.response(400, ErrorSchema)
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
@auth_bp.response(404, ErrorSchema)
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
@auth_bp.response(404, ErrorSchema)
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