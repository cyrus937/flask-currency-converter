# app/routes/user.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.schemas.user_schemas import UserUpdateSchema
from app.middleware.rate_limiter import limiter

user_bp = Blueprint('user', __name__, url_prefix='/api/user')


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Récupération du profil utilisateur détaillé
    ---
    GET /api/user/profile
    Headers: Authorization: Bearer <access_token>
    """
    try:
        from app.models.user import User
        from app.schemas.user_schemas import UserProfileSchema
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        schema = UserProfileSchema()
        return jsonify(schema.dump(user.to_dict(include_sensitive=True))), 200
        
    except Exception as e:
        return jsonify({'error': 'Erreur lors de la récupération du profil'}), 500


@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per hour")
def update_profile():
    """
    Mise à jour du profil utilisateur
    ---
    PUT /api/user/profile
    {
        "first_name": "John",
        "last_name": "Doe",
        "preferred_currency": "EUR"
    }
    """
    schema = UserUpdateSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    try:
        from app.models.user import User
        from app.services.cache_service import CacheService
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Mise à jour des champs
        for field, value in data.items():
            setattr(user, field, value)
        
        user.save()
        
        # Invalider le cache des favoris si la devise préférée a changé
        if 'preferred_currency' in data:
            CacheService.invalidate_user_favorites(user_id)
        
        return jsonify({
            'message': 'Profil mis à jour avec succès',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erreur lors de la mise à jour du profil'}), 500


@user_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """
    Statistiques générales de l'utilisateur
    ---
    GET /api/user/stats
    Headers: Authorization: Bearer <access_token>
    """
    try:
        from app.models.conversion import Conversion
        from app.models.session import Session
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        user_id = get_jwt_identity()
        
        # Statistiques des 30 derniers jours
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Statistiques de conversion
        conversion_stats = Conversion.query.filter(
            Conversion.user_id == user_id,
            Conversion.created_at >= thirty_days_ago
        ).with_entities(
            func.count().label('total_conversions'),
            func.sum(Conversion.original_amount).label('total_volume'),
            func.sum(Conversion.fee_amount).label('total_fees'),
            func.count(func.distinct(Conversion.from_currency)).label('currencies_used')
        ).first()
        
        # Sessions actives
        active_sessions = Session.query.filter_by(
            user_id=user_id,
            is_active=True
        ).count()
        
        return jsonify({
            'period': '30_days',
            'conversions': {
                'total': conversion_stats.total_conversions or 0,
                'volume': float(conversion_stats.total_volume or 0),
                'fees_paid': float(conversion_stats.total_fees or 0),
                'currencies_used': conversion_stats.currencies_used or 0
            },
            'sessions': {
                'active': active_sessions
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erreur lors de la récupération des statistiques'}), 500
