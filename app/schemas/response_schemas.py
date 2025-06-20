# app/schemas/response_schemas.py - Schémas pour les réponses
from marshmallow import Schema, fields


class ErrorSchema(Schema):
    """Schéma pour les erreurs"""
    error = fields.Str(required=True, description="Message d'erreur")
    code = fields.Str(description="Code d'erreur")
    details = fields.Dict(description="Détails supplémentaires")

class MessageSchema(Schema):
    """Schéma pour les messages de succès"""
    message = fields.Str(required=True, description="Message de succès")

class TokenResponseSchema(Schema):
    """Schéma pour les réponses avec tokens"""
    message = fields.Str(required=True)
    access_token = fields.Str(required=True, description="Token d'accès JWT")
    refresh_token = fields.Str(required=True, description="Token de rafraîchissement")
    user = fields.Nested('UserProfileSchema', required=True)
    session_id = fields.Str(description="ID de la session")

class LoginResponseSchema(TokenResponseSchema):
    """Schéma pour la réponse de connexion"""
    pass

class RefreshResponseSchema(Schema):
    """Schéma pour la réponse de rafraîchissement"""
    message = fields.Str(required=True)
    access_token = fields.Str(required=True)
    refresh_token = fields.Str(required=True)

class ConversionListResponseSchema(Schema):
    """Schéma pour la liste des conversions"""
    conversions = fields.List(fields.Nested('ConversionResponseSchema'))

class BatchConversionResponseSchema(Schema):
    """Schéma pour les conversions en lot"""
    conversions = fields.List(fields.Raw())

class ConversionHistoryResponseSchema(Schema):
    """Schéma pour l'historique des conversions"""
    history = fields.List(fields.Nested('ConversionResponseSchema'))
    count = fields.Int(description="Nombre de conversions")

class ConversionStatsSchema(Schema):
    """Schéma pour les statistiques de conversion"""
    period_days = fields.Int()
    total_conversions = fields.Int()
    total_volume = fields.Float()
    total_fees = fields.Float()
    popular_pairs = fields.List(fields.Dict())

class CurrencyRatesResponseSchema(Schema):
    """Schéma pour les taux de change"""
    base = fields.Str(description="Devise de base")
    rates = fields.Dict(description="Taux de change")
    timestamp = fields.DateTime()

class ProvidersStatusSchema(Schema):
    """Schéma pour le statut des providers"""
    providers = fields.Dict()
    available_providers = fields.List(fields.Str())

class SessionSchema(Schema):
    """Schéma pour une session"""
    id = fields.Str()
    device_type = fields.Str()
    ip_address = fields.Str()
    user_agent = fields.Str()
    created_at = fields.DateTime()
    last_activity = fields.DateTime()
    is_current = fields.Bool()

class SessionsResponseSchema(Schema):
    """Schéma pour la liste des sessions"""
    sessions = fields.List(fields.Nested(SessionSchema))

class UserStatsSchema(Schema):
    """Schéma pour les statistiques utilisateur"""
    period = fields.Str()
    conversions = fields.Dict()
    sessions = fields.Dict()