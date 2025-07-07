# app/routes/currencies.py
# import datetime
# from flask import Blueprint, request, jsonify
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from app.models.currency import Currency
# from app.models.exchange_rate import ExchangeRate
# from app.services.rate_fetcher_service import RateFetcherService
# from app.middleware.rate_limiter import limiter
# 
# currencies_bp = Blueprint('currencies', __name__, url_prefix='/api/currencies')
# 
# 
# @currencies_bp.route('', methods=['GET'])
# @limiter.limit("1000 per hour")
# def get_currencies():
#     """
#     Liste des devises supportées
#     ---
#     GET /api/currencies?type=all|fiat|crypto
#     """
#     try:
#         currency_type = request.args.get('type', 'all')
#         
#         query = Currency.query.filter_by(is_active=True)
#         
#         if currency_type == 'fiat':
#             query = query.filter_by(is_crypto=False)
#         elif currency_type == 'crypto':
#             query = query.filter_by(is_crypto=True)
#         
#         currencies = query.order_by(Currency.code).all()
#         
#         return jsonify({
#             'currencies': [currency.to_dict() for currency in currencies],
#             'count': len(currencies)
#         }), 200
#         
#     except Exception as e:
#         return jsonify({'error': 'Erreur lors de la récupération des devises'}), 500
# 
# 
# @currencies_bp.route('/popular', methods=['GET'])
# @limiter.limit("1000 per hour")
# def get_popular_currencies():
#     """
#     Devises populaires
#     ---
#     GET /api/currencies/popular
#     """
#     try:
#         currencies = Currency.get_popular_currencies()
#         
#         return jsonify({
#             'currencies': [currency.to_dict() for currency in currencies]
#         }), 200
#         
#     except Exception as e:
#         return jsonify({'error': 'Erreur lors de la récupération des devises populaires'}), 500
# 
# 
# @currencies_bp.route('/favorites', methods=['GET'])
# @jwt_required()
# def get_favorite_currencies():
#     """
#     Devises favorites de l'utilisateur
#     ---
#     GET /api/currencies/favorites
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
#         favorites = user.get_favorite_currencies()
#         
#         return jsonify({
#             'favorite_currencies': favorites
#         }), 200
#         
#     except Exception as e:
#         return jsonify({'error': 'Erreur lors de la récupération des favoris'}), 500
# 
# 
# @currencies_bp.route('/favorites', methods=['POST'])
# @jwt_required()
# @limiter.limit("100 per hour")
# def add_favorite_currency():
#     """
#     Ajouter une devise aux favoris
#     ---
#     POST /api/currencies/favorites
#     {
#         "currency_code": "EUR"
#     }
#     """
#     try:
#         from app.models.user import User
#         
#         data = request.json
#         currency_code = data.get('currency_code')
#         
#         if not currency_code:
#             return jsonify({'error': 'Code de devise requis'}), 400
#         
#         # Vérifier que la devise existe
#         currency = Currency.find_by_code(currency_code)
#         if not currency:
#             return jsonify({'error': 'Devise non supportée'}), 400
#         
#         user_id = get_jwt_identity()
#         user = User.query.get(user_id)
#         
#         user.add_favorite_currency(currency_code)
#         
#         return jsonify({'message': 'Devise ajoutée aux favoris'}), 200
#         
#     except Exception as e:
#         return jsonify({'error': 'Erreur lors de l\'ajout aux favoris'}), 500
# 
# 
# @currencies_bp.route('/favorites/<currency_code>', methods=['DELETE'])
# @jwt_required()
# def remove_favorite_currency(currency_code):
#     """
#     Supprimer une devise des favoris
#     ---
#     DELETE /api/currencies/favorites/<currency_code>
#     Headers: Authorization: Bearer <access_token>
#     """
#     try:
#         from app.models.user import User
#         
#         user_id = get_jwt_identity()
#         user = User.query.get(user_id)
#         
#         user.remove_favorite_currency(currency_code)
#         
#         return jsonify({'message': 'Devise supprimée des favoris'}), 200
#         
#     except Exception as e:
#         return jsonify({'error': 'Erreur lors de la suppression des favoris'}), 500
# 
# 
# @currencies_bp.route('/rates', methods=['GET'])
# @limiter.limit("1000 per hour")
# def get_latest_rates():
#     """
#     Taux de change actuels
#     ---
#     GET /api/currencies/rates?base=USD&symbols=EUR,GBP,JPY
#     """
#     try:
#         base_currency = request.args.get('base', 'USD').upper()
#         symbols = request.args.get('symbols', '').upper().split(',')
#         symbols = [s.strip() for s in symbols if s.strip()]
#         
#         # Si aucun symbole spécifié, récupérer les taux populaires
#         if not symbols:
#             symbols = ['EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD']
#         
#         rates = {}
#         rate_fetcher = RateFetcherService()
#         
#         for symbol in symbols:
#             if symbol != base_currency:
#                 try:
#                     rate = rate_fetcher.fetch_rate(base_currency, symbol)
#                     rates[symbol] = float(rate)
#                 except Exception:
#                     # Essayer depuis la base de données
#                     db_rate = ExchangeRate.get_latest_rate(base_currency, symbol)
#                     if db_rate:
#                         rates[symbol] = float(db_rate.rate)
#         
#         return jsonify({
#             'base': base_currency,
#             'rates': rates,
#             'timestamp': datetime.utcnow().isoformat()
#         }), 200
#         
#     except Exception as e:
#         return jsonify({'error': 'Erreur lors de la récupération des taux'}), 500
# 
# 
# @currencies_bp.route('/providers/status', methods=['GET'])
# @limiter.limit("100 per hour")
# def get_providers_status():
#     """
#     Statut des providers de taux
#     ---
#     GET /api/currencies/providers/status
#     """
#     try:
#         rate_fetcher = RateFetcherService()
#         status = rate_fetcher.test_providers()
#         
#         return jsonify({
#             'providers': status,
#             'available_providers': rate_fetcher.get_available_providers()
#         }), 200
#         
#     except Exception as e:
#         return jsonify({'error': 'Erreur lors de la vérification des providers'}), 500

from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from app.models.currency import Currency
from app.models.exchange_rate import ExchangeRate
from app.services.rate_fetcher_service import RateFetcherService
from app.schemas.currency_schemas import CurrencySchema, CurrencyListSchema
from app.schemas.response_schemas import (
    CurrencyRatesResponseSchema, ProvidersStatusSchema, MessageSchema
)
from app.middleware.rate_limiter import limiter
from datetime import datetime

currencies_bp = Blueprint(
    'currencies', 
    __name__, 
    url_prefix='/api/currencies',
    description='Gestion des devises et taux de change'
)

@currencies_bp.route('', methods=['GET'])
@currencies_bp.response(200, CurrencyListSchema)
@currencies_bp.doc(
    summary="Liste des devises supportées",
    description="""
Retourne la liste de toutes les devises supportées par l'API.

**Filtres disponibles :**
- `type=fiat` : Devises traditionnelles uniquement
- `type=crypto` : Cryptomonnaies uniquement  
- `type=all` : Toutes les devises (défaut)

**40+ devises supportées :**
- Devises majeures : USD, EUR, GBP, JPY, CHF, CAD, AUD
- Devises asiatiques : CNY, INR, KRW, SGD, HKD, JPY
- Devises européennes : NOK, SEK, DKK, PLN, CZK
- Cryptomonnaies : BTC, ETH, LTC, ADA, DOT
    """,
    tags=['Currencies']
)
@limiter.limit("1000 per hour")
def get_currencies():
    """Liste des devises supportées"""
    try:
        currency_type = request.args.get('type', 'all')
        
        query = Currency.query.filter_by(is_active=True)
        
        if currency_type == 'fiat':
            query = query.filter_by(is_crypto=False)
        elif currency_type == 'crypto':
            query = query.filter_by(is_crypto=True)
        
        currencies = query.order_by(Currency.code).all()
        
        return {
            'currencies': [currency.to_dict() for currency in currencies],
            'count': len(currencies)
        }
        
    except Exception:
        abort(500, message='Erreur lors de la récupération des devises')


@currencies_bp.route('/popular', methods=['GET'])
@currencies_bp.response(200, CurrencyListSchema)
@currencies_bp.doc(
    summary="Devises populaires",
    description="Retourne les devises les plus utilisées et échangées",
    tags=['Currencies']
)
@limiter.limit("1000 per hour")
def get_popular_currencies():
    """Devises populaires"""
    try:
        currencies = Currency.get_popular_currencies()
        
        return {
            'currencies': [currency.to_dict() for currency in currencies]
        }
        
    except Exception:
        abort(500, message='Erreur lors de la récupération des devises populaires')


@currencies_bp.route('/rates', methods=['GET'])
@currencies_bp.response(200, CurrencyRatesResponseSchema)
@currencies_bp.doc(
    summary="Taux de change actuels",
    description="""
Récupère les taux de change en temps réel pour une devise de base.

**Paramètres :**
- `base` : Devise de base (défaut: USD)
- `symbols` : Devises cibles séparées par des virgules (ex: EUR,GBP,JPY)

**Exemple :**
`GET /api/currencies/rates?base=USD&symbols=EUR,GBP,JPY`
    """,
    tags=['Currencies']
)
@limiter.limit("1000 per hour")
def get_latest_rates():
    """Taux de change actuels"""
    try:
        base_currency = request.args.get('base', 'USD').upper()
        symbols = request.args.get('symbols', '').upper().split(',')
        symbols = [s.strip() for s in symbols if s.strip()]
        
        if not symbols:
            symbols = ['EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD']
        
        rates = {}
        rate_fetcher = RateFetcherService()
        
        for symbol in symbols:
            if symbol != base_currency:
                try:
                    rate = rate_fetcher.fetch_rate(base_currency, symbol)
                    rates[symbol] = float(rate)
                except Exception:
                    db_rate = ExchangeRate.get_latest_rate(base_currency, symbol)
                    if db_rate:
                        rates[symbol] = float(db_rate.rate)
        
        return {
            'base': base_currency,
            'rates': rates,
            'timestamp': datetime.utcnow()
        }
        
    except Exception:
        abort(500, message='Erreur lors de la récupération des taux')


@currencies_bp.route('/providers/status', methods=['GET'])
@currencies_bp.response(200, ProvidersStatusSchema)
@currencies_bp.doc(
    summary="Statut des providers",
    description="Vérifie le statut et la disponibilité des providers de taux de change",
    tags=['Currencies']
)
@limiter.limit("100 per hour")
def get_providers_status():
    """Statut des providers de taux"""
    try:
        rate_fetcher = RateFetcherService()
        status = rate_fetcher.test_providers()
        
        return {
            'providers': status,
            'available_providers': rate_fetcher.get_available_providers()
        }
        
    except Exception:
        abort(500, message='Erreur lors de la vérification des providers')


@currencies_bp.route('/favorites', methods=['GET'])
@currencies_bp.doc(security=[{"bearerAuth": []}])
@currencies_bp.response(200, schema={'type': 'object', 'properties': {'favorite_currencies': {'type': 'array', 'items': {'type': 'string'}}}})
@currencies_bp.doc(
    summary="Devises favorites",
    description="Récupère les devises favorites de l'utilisateur connecté",
    tags=['Currencies']
)
@jwt_required()
def get_favorite_currencies():
    """Devises favorites utilisateur"""
    try:
        from app.models.user import User
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            abort(404, message='Utilisateur non trouvé')
        
        favorites = user.get_favorite_currencies()
        
        return {
            'favorite_currencies': favorites
        }
        
    except Exception:
        abort(500, message='Erreur lors de la récupération des favoris')


@currencies_bp.route('/favorites', methods=['POST'])
@currencies_bp.doc(security=[{"bearerAuth": []}])
@currencies_bp.arguments(schema={'type': 'object', 'properties': {'currency_code': {'type': 'string'}}}, location='json')
@currencies_bp.response(200, MessageSchema)
@currencies_bp.doc(
    summary="Ajouter devise favorite",
    description="Ajoute une devise aux favoris de l'utilisateur",
    tags=['Currencies']
)
@jwt_required()
@limiter.limit("100 per hour")
def add_favorite_currency(args):
    """Ajouter devise aux favoris"""
    try:
        from app.models.user import User
        
        currency_code = args.get('currency_code')
        
        if not currency_code:
            abort(400, message='Code de devise requis')
        
        currency = Currency.find_by_code(currency_code)
        if not currency:
            abort(400, message='Devise non supportée')
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        user.add_favorite_currency(currency_code)
        
        return {'message': 'Devise ajoutée aux favoris'}
        
    except Exception:
        abort(500, message='Erreur lors de l\'ajout aux favoris')


@currencies_bp.route('/favorites/<currency_code>', methods=['DELETE'])
@currencies_bp.doc(security=[{"bearerAuth": []}])
@currencies_bp.response(200, MessageSchema)
@currencies_bp.doc(
    summary="Supprimer devise favorite",
    description="Supprime une devise des favoris de l'utilisateur",
    tags=['Currencies']
)
@jwt_required()
def remove_favorite_currency(currency_code):
    """Supprimer devise des favoris"""
    try:
        from app.models.user import User
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        user.remove_favorite_currency(currency_code)
        
        return {'message': 'Devise supprimée des favoris'}
        
    except Exception:
        abort(500, message='Erreur lors de la suppression des favoris')