# app/routes/dashboard.py
from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.conversion import Conversion
from app.models.currency import Currency
from app.services.conversion_service import ConversionService

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@jwt_required()
def dashboard_home():
    """
    Dashboard principal (interface web)
    ---
    GET /dashboard/
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return render_template('error.html', message='Utilisateur non trouvé'), 404
        
        # Données pour le dashboard
        recent_conversions = Conversion.get_user_history(user_id, limit=5)
        popular_currencies = Currency.get_popular_currencies()
        user_favorites = user.get_favorite_currencies()
        
        return render_template('dashboard/home.html', 
                             user=user, 
                             recent_conversions=recent_conversions,
                             popular_currencies=popular_currencies,
                             user_favorites=user_favorites)
        
    except Exception as e:
        return render_template('error.html', message='Erreur lors du chargement du dashboard'), 500


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
