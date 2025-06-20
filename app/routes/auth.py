# app/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError
from app.services.auth_service import AuthService
from app.schemas.auth_schemas import (
    RegisterSchema, LoginSchema, RefreshTokenSchema, 
    ChangePasswordSchema
)
from app.middleware.rate_limiter import limiter
from app.utils.exceptions import AuthenticationError, ValidationError as CustomValidationError

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """
    Enregistrement d'un nouvel utilisateur
    ---
    POST /api/auth/register
    {
        "email": "user@example.com",
        "password": "password123",
        "first_name": "John",
        "last_name": "Doe",
        "preferred_currency": "USD"
    }
    """
    schema = RegisterSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    try:
        user = AuthService.register_user(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            preferred_currency=data.get('preferred_currency', 'USD')
        )
        
        return jsonify({
            'message': 'Utilisateur créé avec succès',
            'user': user.to_dict()
        }), 201
        
    except (AuthenticationError, CustomValidationError) as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Erreur lors de la création du compte'}), 500


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """
    Connexion utilisateur
    ---
    POST /api/auth/login
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    schema = LoginSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    try:
        result = AuthService.authenticate_user(
            email=data['email'],
            password=data['password'],
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        return jsonify({
            'message': 'Connexion réussie',
            'user': result['user'].to_dict(),
            'access_token': result['access_token'],
            'refresh_token': result['refresh_token'],
            'session_id': result['session'].id
        }), 200
        
    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': 'Erreur lors de la connexion'}), 500


@auth_bp.route('/refresh', methods=['POST'])
@limiter.limit("20 per minute")
def refresh():
    """
    Rafraîchissement des tokens
    ---
    POST /api/auth/refresh
    {
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
    """
    schema = RefreshTokenSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    try:
        from flask_jwt_extended import decode_token
        
        # Décoder le refresh token pour extraire les infos
        decoded_token = decode_token(data['refresh_token'])
        user_id = decoded_token['sub']
        jti = decoded_token['jti']
        
        result = AuthService.refresh_tokens(jti, user_id)
        
        return jsonify({
            'message': 'Tokens rafraîchis',
            'access_token': result['access_token'],
            'refresh_token': result['refresh_token']
        }), 200
        
    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': 'Erreur lors du rafraîchissement'}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Déconnexion utilisateur
    ---
    POST /api/auth/logout
    Headers: Authorization: Bearer <access_token>
    """
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        session_id = claims.get('session_id')
        
        AuthService.logout_user(user_id, session_id)
        
        return jsonify({'message': 'Déconnexion réussie'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Erreur lors de la déconnexion'}), 500


@auth_bp.route('/logout-all', methods=['POST'])
@jwt_required()
def logout_all():
    """
    Déconnexion de toutes les sessions
    ---
    POST /api/auth/logout-all
    Headers: Authorization: Bearer <access_token>
    """
    try:
        user_id = get_jwt_identity()
        AuthService.logout_user(user_id)  # Sans session_id = toutes les sessions
        
        return jsonify({'message': 'Déconnexion de toutes les sessions réussie'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Erreur lors de la déconnexion'}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
@limiter.limit("3 per minute")
def change_password():
    """
    Changement de mot de passe
    ---
    POST /api/auth/change-password
    {
        "current_password": "oldpassword",
        "new_password": "newpassword"
    }
    """
    schema = ChangePasswordSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    try:
        user_id = get_jwt_identity()
        
        AuthService.change_password(
            user_id=user_id,
            current_password=data['current_password'],
            new_password=data['new_password']
        )
        
        return jsonify({'message': 'Mot de passe modifié avec succès'}), 200
        
    except (AuthenticationError, CustomValidationError) as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Erreur lors du changement de mot de passe'}), 500


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Récupération du profil utilisateur
    ---
    GET /api/auth/profile
    Headers: Authorization: Bearer <access_token>
    """
    try:
        from app.models.user import User
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        return jsonify({
            'user': user.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erreur lors de la récupération du profil'}), 500


@auth_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    """
    Liste des sessions actives
    ---
    GET /api/auth/sessions
    Headers: Authorization: Bearer <access_token>
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
                'created_at': session.created_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'is_current': session.id == get_jwt().get('session_id')
            })
        
        return jsonify({'sessions': sessions_data}), 200
        
    except Exception as e:
        return jsonify({'error': 'Erreur lors de la récupération des sessions'}), 500


@auth_bp.route('/sessions/<session_id>', methods=['DELETE'])
@jwt_required()
def delete_session(session_id):
    """
    Suppression d'une session spécifique
    ---
    DELETE /api/auth/sessions/<session_id>
    Headers: Authorization: Bearer <access_token>
    """
    try:
        from app.services.session_service import SessionService
        
        user_id = get_jwt_identity()
        
        # Vérifier que la session appartient à l'utilisateur
        from app.models.session import Session
        session = Session.query.filter_by(id=session_id, user_id=user_id).first()
        
        if not session:
            return jsonify({'error': 'Session non trouvée'}), 404
        
        SessionService.deactivate_session(session_id)
        
        return jsonify({'message': 'Session supprimée'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Erreur lors de la suppression de la session'}), 500
