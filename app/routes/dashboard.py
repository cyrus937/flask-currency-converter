# app/routes/dashboard.py
from typing import Any
from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import decode_token, jwt_required, get_jwt_identity
from app.models.user import User
from app.models.conversion import Conversion
from app.models.currency import Currency
from app.schemas.dashboard_schemas import GeneralResponseSchema
from app.schemas.response_schemas import ConversionHistoryResponseSchema
from app.services.conversion_service import ConversionService
from flask_smorest import Blueprint as BL, abort

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

api_dashboard = BL(
    'api_dashboard', 
    __name__, 
    url_prefix='/api/dashboard',
    description='Conversion de devises en temps réel'
)

@api_dashboard.route('/general', methods=['GET'])
@api_dashboard.doc(security=[{"bearerAuth": []}])
@api_dashboard.response(200, GeneralResponseSchema)
@api_dashboard.doc(
    summary="Historique des conversions",
    description="Récupère l'historique des conversions de l'utilisateur connecté",
    tags=['Dashboard']
)
@jwt_required()
def get_conversion_history():
    """Historique des conversions utilisateur"""
    try:
        user_id = get_jwt_identity()
        user: User = User.query.get(user_id)

        recent_conversions = Conversion.get_user_history(user_id, limit=5)
        popular_currencies = Currency.get_popular_currencies()
        # user_favorites = user.get_favorite_currencies()
        
        return {
            user: user.to_dict(include_sensitive=True),
            'recent_conversions': [conv.to_dict() for conv in recent_conversions],
            'popular_currencies': [currency.to_dict() for currency in popular_currencies],
            # 'user_favorites': user_favorites
        }
        
    except Exception as e:
        abort(500, message='Erreur lors de la récupération de l\'historique: ' + str(e))


@dashboard_bp.route('/')
# @jwt_required()
def dashboard_home():
    """
    Dashboard principal (interface web)
    ---
    GET /dashboard/
    """
    try:
        print("Loading dashboard home...")  # Debugging line
        return render_template('dashboard/home.html'
                            #  user=user, 
                            #  recent_conversions=recent_conversions,
                            #  popular_currencies=popular_currencies,
                            #  user_favorites=user_favorites
                            )
        
    except Exception as e:
        print(f"Error loading dashboard: {e}")
        return render_template('errors/500.html', message='Erreur lors du chargement du dashboard'), 500

@dashboard_bp.route('/converter')
@jwt_required()
def currency_converter():
    """
    Interface de conversion de devises
    ---
    GET /dashboard/converter
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        currencies = Currency.get_active_currencies()
        user_favorites = user.get_favorite_currencies() if user else []
        
        return render_template('dashboard/converter.html',
                             user=user,
                             currencies=currencies,
                             user_favorites=user_favorites)
        
    except Exception as e:
        return render_template('error.html', message='Erreur lors du chargement du convertisseur'), 500


@dashboard_bp.route('/history')
@jwt_required()
def conversion_history():
    """
    Historique des conversions
    ---
    GET /dashboard/history
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        conversions = Conversion.query.filter_by(user_id=user_id)\
                                    .order_by(Conversion.created_at.desc())\
                                    .paginate(page=page, per_page=per_page, error_out=False)
        
        return render_template('dashboard/history.html',
                             user=user,
                             conversions=conversions)
        
    except Exception as e:
        return render_template('error.html', message='Erreur lors du chargement de l\'historique'), 500


@dashboard_bp.route('/api/quick-convert', methods=['POST'])
@jwt_required()
def quick_convert():
    """
    API de conversion rapide pour le dashboard
    ---
    POST /dashboard/api/quick-convert
    """
    try:
        data = request.json
        user_id = get_jwt_identity()
        
        conversion_service = ConversionService()
        result = conversion_service.convert(
            amount=data['amount'],
            from_currency=data['from_currency'],
            to_currency=data['to_currency'],
            user_id=user_id
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400
