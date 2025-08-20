from marshmallow import Schema, fields

from app.schemas.currency_schemas import CurrencySchema


class GeneralResponseSchema(Schema):
    """Schéma pour la réponse de conversion"""
    user = fields.Nested('UserProfileSchema', required=True)
    recent_conversions = fields.List(fields.Nested('ConversionResponseSchema'))
    popular_currencies = fields.List(fields.Nested(CurrencySchema))