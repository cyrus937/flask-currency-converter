# app/schemas/currency_schemas.py
from marshmallow import Schema, fields


class CurrencySchema(Schema):
    """Schéma pour une devise"""
    id = fields.Str()
    code = fields.Str()
    name = fields.Str()
    symbol = fields.Str()
    decimal_places = fields.Int()
    is_crypto = fields.Bool()
    country_code = fields.Str(allow_none=True)


class CurrencyListSchema(Schema):
    """Schéma pour une liste de devises"""
    currencies = fields.List(fields.Nested(CurrencySchema))
    count = fields.Int()
