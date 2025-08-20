# app/schemas/conversion_schemas.py
from marshmallow import Schema, fields, validate, validates, ValidationError
from decimal import Decimal


class ConversionRequestSchema(Schema):
    """Schéma pour une demande de conversion"""
    amount = fields.Float(required=True, validate=validate.Range(min=0.01, max=1000000000))
    from_currency = fields.Str(required=True, validate=validate.Length(equal=3))
    to_currency = fields.Str(required=True, validate=validate.Length(equal=3))
    
    @validates('from_currency')
    def validate_from_currency(self, value):
        if not value.isupper():
            raise ValidationError('Le code de devise doit être en majuscules')
    
    @validates('to_currency')
    def validate_to_currency(self, value):
        if not value.isupper():
            raise ValidationError('Le code de devise doit être en majuscules')

class BatchConversionRequestSchema(Schema):
    """Schéma pour une demande de conversion en lot"""
    amount = fields.Float(required=True, validate=validate.Range(min=0.01, max=1000000000))
    from_currency = fields.Str(required=True, validate=validate.Length(equal=3))
    to_currencies = fields.List(fields.Str(validate=validate.Length(equal=3)), required=True, validate=validate.Length(max=10))
    
    @validates('from_currency')
    def validate_from_currency(self, value):
        if not value.isupper():
            raise ValidationError('Le code de devise doit être en majuscules')
    
    @validates('to_currencies')
    def validate_to_currencies(self, value):
        for currency in value:
            if not currency.isupper():
                raise ValidationError('Tous les codes de devise doivent être en majuscules')
        if len(value) > 10:
            raise ValidationError('Le nombre maximum de devises cibles est 10')


class ConversionResponseSchema(Schema):
    """Schéma pour la réponse de conversion"""
    conversion_id = fields.Str()
    original_amount = fields.Float()
    gross_amount = fields.Float()
    converted_amount = fields.Float()
    net_amount = fields.Float()
    exchange_rate = fields.Float()
    from_currency = fields.Str()
    to_currency = fields.Str()
    fee_amount = fields.Float()
    fee_rate = fields.Float()
    provider = fields.Str()
    timestamp = fields.DateTime()
