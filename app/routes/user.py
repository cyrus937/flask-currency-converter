# # app/routes/user.py 

from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.user_schemas import UserUpdateSchema, UserProfileSchema
from app.schemas.response_schemas import MessageSchema, UserStatsSchema
from app.middleware.rate_limiter import limiter

user_bp = Blueprint(
    'user', 
    __name__, 
    url_prefix='/api/user',
    description='Gestion du profil utilisateur'
)

@user_bp.route('/profile', methods=['GET'])
@user_bp.doc(security=[{"bearerAuth": []}])
@user_bp.response(200, UserProfileSchema)
@user_bp.doc(
    summary="Profil utilisateur détaillé",
    description="Récupère toutes les informations du profil utilisateur avec statistiques",
    tags=['User']
)
@jwt_required()
def get_profile():
    """Profil utilisateur détaillé"""
    try:
        from app.models.user import User
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            abort(404, message='Utilisateur non trouvé')
        
        return user.to_dict(include_sensitive=True)
        
    except Exception:
        abort(500, message='Erreur lors de la récupération du profil')


@user_bp.route('/profile', methods=['PUT'])
@user_bp.doc(security=[{"bearerAuth": []}])
@user_bp.arguments(UserUpdateSchema, location='json')
@user_bp.response(200, UserProfileSchema)
@user_bp.doc(
    summary="Mise à jour profil",
    description="""
Met à jour les informations du profil utilisateur

Limites :
- 10 requêtes par heure
    """,
    tags=['User']
)
@jwt_required()
@limiter.limit("10 per hour")
def update_profile(args):
    """Mise à jour du profil"""
    try:
        from app.models.user import User
        from app.services.cache_service import CacheService
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            abort(404, message='Utilisateur non trouvé')
        
        for field, value in args.items():
            setattr(user, field, value)
        
        user.save()
        
        if 'preferred_currency' in args:
            CacheService.invalidate_user_favorites(user_id)
        
        return user.to_dict()
        
    except Exception:
        abort(500, message='Erreur lors de la mise à jour du profil')


@user_bp.route('/stats', methods=['GET'])
@user_bp.doc(security=[{"bearerAuth": []}])
@user_bp.response(200, UserStatsSchema)
@user_bp.doc(
    summary="Statistiques utilisateur",
    description="Statistiques d'activité de l'utilisateur les 30 derniers jours (conversions, sessions, etc.)",
    tags=['User']
)
@jwt_required()
def get_user_stats():
    """Statistiques utilisateur"""
    try:
        from app.models.conversion import Conversion
        from app.models.session import Session
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        user_id = get_jwt_identity()
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        conversion_stats = Conversion.query.filter(
            Conversion.user_id == user_id,
            Conversion.created_at >= thirty_days_ago
        ).with_entities(
            func.count().label('total_conversions'),
            func.sum(Conversion.original_amount).label('total_volume'),
            func.sum(Conversion.fee_amount).label('total_fees'),
            func.count(func.distinct(Conversion.from_currency)).label('currencies_used')
        ).first()
        
        active_sessions = Session.query.filter_by(
            user_id=user_id,
            is_active=True
        ).count()
        
        return {
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
        }
        
    except Exception:
        abort(500, message='Erreur lors de la récupération des statistiques')