# app/routes/conversions.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_required
from marshmallow import ValidationError
from app.services.conversion_service import ConversionService
from app.schemas.conversion_schemas import ConversionRequestSchema, ConversionResponseSchema
from app.middleware.rate_limiter import limiter
from app.utils.exceptions import CurrencyError, ValidationError as CustomValidationError

conversions_bp = Blueprint('conversions', __name__, url_prefix='/api/conversions')


@conversions_bp.route('/convert', methods=['POST'])
@limiter.limit("100 per hour")
def convert_currency():
    """
    Conversion de devise
    ---
    POST /api/conversions/convert
    {
        "amount": 100.00,
        "from_currency": "USD",
        "to_currency": "EUR"
    }
    """
    schema = ConversionRequestSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    try:
        # Récupérer l'utilisateur si authentifié
        user_id = None
        try:
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
        except:
            pass  # Utilisateur non authentifié, c'est OK
        
        conversion_service = ConversionService()
        result = conversion_service.convert(
            amount=data['amount'],
            from_currency=data['from_currency'],
            to_currency=data['to_currency'],
            user_id=user_id
        )
        
        response_schema = ConversionResponseSchema()
        return jsonify(response_schema.dump(result)), 200
        
    except (CurrencyError, CustomValidationError) as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Erreur lors de la conversion'}), 500


@conversions_bp.route('/batch', methods=['POST'])
@limiter.limit("20 per hour")
def batch_convert():
    """
    Conversion en lot
    ---
    POST /api/conversions/batch
    {
        "amount": 100.00,
        "from_currency": "USD",
        "to_currencies": ["EUR", "GBP", "JPY"]
    }
    """
    try:
        data = request.json
        amount = data.get('amount')
        from_currency = data.get('from_currency')
        to_currencies = data.get('to_currencies', [])
        
        if not amount or not from_currency or not to_currencies:
            return jsonify({'error': 'Paramètres manquants'}), 400
        
        if len(to_currencies) > 10:
            return jsonify({'error': 'Maximum 10 devises de destination'}), 400
        
        # Récupérer l'utilisateur si authentifié
        user_id = None
        try:
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
        except:
            pass
        
        conversion_service = ConversionService()
        results = []
        
        for to_currency in to_currencies:
            try:
                result = conversion_service.convert(
                    amount=amount,
                    from_currency=from_currency,
                    to_currency=to_currency,
                    user_id=user_id
                )
                results.append(result)
            except Exception as e:
                results.append({
                    'from_currency': from_currency,
                    'to_currency': to_currency,
                    'error': str(e)
                })
        
        return jsonify({'conversions': results}), 200
        
    except Exception as e:
        return jsonify({'error': 'Erreur lors de la conversion en lot'}), 500


@conversions_bp.route('/history', methods=['GET'])
@jwt_required()
def get_conversion_history():
    """
    Historique des conversions de l'utilisateur
    ---
    GET /api/conversions/history?limit=50
    Headers: Authorization: Bearer <access_token>
    """
    try:
        user_id = get_jwt_identity()
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100
        
        conversion_service = ConversionService()
        history = conversion_service.get_user_conversion_history(user_id, limit)
        
        return jsonify({
            'history': history,
            'count': len(history)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erreur lors de la récupération de l\'historique'}), 500


@conversions_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_conversion_stats():
    """
    Statistiques de conversion de l'utilisateur
    ---
    GET /api/conversions/stats?days=30
    Headers: Authorization: Bearer <access_token>
    """
    try:
        user_id = get_jwt_identity()
        days = min(int(request.args.get('days', 30)), 365)  # Max 1 an
        
        from app.models.conversion import Conversion
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Statistiques générales
        stats = Conversion.query.filter(
            Conversion.user_id == user_id,
            Conversion.created_at >= start_date
        ).with_entities(
            func.count().label('total_conversions'),
            func.sum(Conversion.original_amount).label('total_volume'),
            func.sum(Conversion.fee_amount).label('total_fees')
        ).first()
        
        # Paires les plus utilisées
        popular_pairs = Conversion.query.filter(
            Conversion.user_id == user_id,
            Conversion.created_at >= start_date
        ).with_entities(
            Conversion.from_currency,
            Conversion.to_currency,
            func.count().label('count')
        ).group_by(
            Conversion.from_currency,
            Conversion.to_currency
        ).order_by(func.count().desc()).limit(5).all()
        
        return jsonify({
            'period_days': days,
            'total_conversions': stats.total_conversions or 0,
            'total_volume': float(stats.total_volume or 0),
            'total_fees': float(stats.total_fees or 0),
            'popular_pairs': [
                {
                    'from_currency': pair.from_currency,
                    'to_currency': pair.to_currency,
                    'count': pair.count
                }
                for pair in popular_pairs
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erreur lors de la récupération des statistiques'}), 500
