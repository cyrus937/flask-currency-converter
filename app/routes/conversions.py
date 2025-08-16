# app/routes/conversions.py
import http
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from app.services.conversion_service import ConversionService
from app.schemas.conversion_schemas import (
    BatchConversionRequestSchema,
    ConversionRequestSchema,
    ConversionResponseSchema,
)
from app.schemas.response_schemas import (
    ConversionHistoryResponseSchema,
    ConversionStatsSchema,
    BatchConversionResponseSchema,
    ErrorSchema,
)
from app.middleware.rate_limiter import limiter
from app.utils.exceptions import CurrencyError, ValidationError as CustomValidationError

conversions_bp = Blueprint(
    "conversions",
    __name__,
    url_prefix="/api/conversions",
    description="Conversion de devises en temps réel",
)


@conversions_bp.route("/convert", methods=["POST"])
@conversions_bp.arguments(ConversionRequestSchema, location="json")
@conversions_bp.response(200, ConversionResponseSchema)
@conversions_bp.alt_response(
    400,
    http.HTTPStatus(400).name,
    schema=ErrorSchema,
    description="Paramètres invalides",
)
@conversions_bp.doc(
    summary="Conversion de devise",
    description="""
Convertit un montant d'une devise vers une autre en utilisant les taux en temps réel.""",
    tags=["Conversions"],
    security=[{"bearerAuth": []}],
)
@jwt_required()
@limiter.limit("100 per hour")
def convert_currency(args):
    """Conversion de devise simple"""
    try:
        # Récupérer l'utilisateur si authentifié
        user_id = None
        try:
            from flask_jwt_extended import verify_jwt_in_request

            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
        except:
            pass

        conversion_service = ConversionService()
        result = conversion_service.convert(
            amount=args["amount"],
            from_currency=args["from_currency"],
            to_currency=args["to_currency"],
            user_id=user_id,
        )

        return result

    except (CurrencyError, CustomValidationError) as e:
        abort(400, errors=e.__dict__, message=str(e.message))
    except Exception:
        abort(500, message="Erreur lors de la conversion")


@conversions_bp.route("/batch", methods=["POST"])
@conversions_bp.arguments(BatchConversionRequestSchema, location="json")
@conversions_bp.response(200, BatchConversionResponseSchema)
@conversions_bp.alt_response(
    400,
    http.HTTPStatus(400).name,
    schema=ErrorSchema,
    description="Paramètres invalides",
)
@conversions_bp.alt_response(
    500, http.HTTPStatus(500).name, schema=ErrorSchema, description="Erreur interne"
)
@conversions_bp.doc(
    summary="Conversion en lot",
    description="Convertit un montant vers plusieurs devises simultanément (max 10 devises)",
    tags=["Conversions"],
    security=[{"bearerAuth": []}],
)
@jwt_required()
@limiter.limit("50 per hour")
def batch_convert(args):
    """Conversion vers plusieurs devises"""
    try:
        amount = args["amount"]
        from_currency = args["from_currency"]
        # to_currencies = args['to_currencies'] if 'to_currencies' in args else []
        to_currencies = args.get("to_currencies", [])

        if not amount or not from_currency or not to_currencies:
            abort(400, message="Paramètres manquants")

        if len(to_currencies) > 10:
            abort(400, message="Maximum 10 devises de destination")

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
                    user_id=user_id,
                )
                results.append(result)
            except Exception as e:
                results.append(
                    {
                        "from_currency": from_currency,
                        "to_currency": to_currency,
                        "error": str(e),
                    }
                )

        return {"conversions": results}

    except Exception:
        abort(500, message="Erreur lors de la conversion en lot")


@conversions_bp.route("/history", methods=["GET"])
@conversions_bp.doc(security=[{"bearerAuth": []}])
@conversions_bp.response(200, ConversionHistoryResponseSchema)
@conversions_bp.alt_response(
    500, http.HTTPStatus(500).name, schema=ErrorSchema, description="Erreur interne"
)
@conversions_bp.doc(
    summary="Historique des conversions",
    description="""Récupère l'historique des conversions de l'utilisateur connecté
    
    **Paramètres :**
    - `limit` : Limite du nombre de résultats (défaut: 50)

    **Exemple :**
    `GET /api/conversions/history?limit=50`

    """,
    tags=["Conversions"],
)
@jwt_required()
def get_conversion_history():
    """Historique des conversions utilisateur"""
    try:
        user_id = get_jwt_identity()
        limit = min(int(request.args.get("limit", 50)), 100)

        conversion_service = ConversionService()
        history = conversion_service.get_user_conversion_history(user_id, limit)

        return {"history": history, "count": len(history)}

    except Exception:
        abort(500, message="Erreur lors de la récupération de l'historique")


@conversions_bp.route("/stats", methods=["GET"])
@conversions_bp.doc(security=[{"bearerAuth": []}])
@conversions_bp.response(200, ConversionStatsSchema)
@conversions_bp.alt_response(
    400,
    http.HTTPStatus(400).name,
    schema=ErrorSchema,
    description="Paramètres invalides",
)
@conversions_bp.alt_response(
    500, http.HTTPStatus(500).name, schema=ErrorSchema, description="Erreur interne"
)
@conversions_bp.doc(
    summary="Statistiques de conversion",
    description="""Statistiques personnalisées des conversions de l'utilisateur
    
    **Paramètres :**
    - `days` : Nombre de jours pour les statistiques (défaut: 30)

    **Exemple :**
    `GET /api/conversions/stats?days=30`

    """,
    tags=["Conversions"],
)
@jwt_required()
def get_conversion_stats():
    """Statistiques de conversion utilisateur"""
    try:
        user_id = get_jwt_identity()
        days = min(int(request.args.get("days", 30)), 365)

        from app.models.conversion import Conversion
        from sqlalchemy import func
        from datetime import datetime, timedelta

        start_date = datetime.utcnow() - timedelta(days=days)

        stats = (
            Conversion.query.filter(
                Conversion.user_id == user_id, Conversion.created_at >= start_date
            )
            .with_entities(
                func.count().label("total_conversions"),
                func.sum(Conversion.original_amount).label("total_volume"),
                func.sum(Conversion.fee_amount).label("total_fees"),
            )
            .first()
        )

        popular_pairs = (
            Conversion.query.filter(
                Conversion.user_id == user_id, Conversion.created_at >= start_date
            )
            .with_entities(
                Conversion.from_currency,
                Conversion.to_currency,
                func.count().label("count"),
            )
            .group_by(Conversion.from_currency, Conversion.to_currency)
            .order_by(func.count().desc())
            .limit(5)
            .all()
        )

        return {
            "period_days": days,
            "total_conversions": stats.total_conversions or 0,
            "total_volume": float(stats.total_volume or 0),
            "total_fees": float(stats.total_fees or 0),
            "popular_pairs": [
                {
                    "from_currency": pair.from_currency,
                    "to_currency": pair.to_currency,
                    "count": pair.count,
                }
                for pair in popular_pairs
            ],
        }

    except Exception:
        abort(500, message="Erreur lors de la récupération des statistiques")
