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
    countries_code = fields.Str(allow_none=True)


class CurrencyListSchema(Schema):
    """Schéma pour une liste de devises"""

    currencies = fields.List(fields.Nested(CurrencySchema))
    count = fields.Int()


class FavoriteCurrenciesSchema(Schema):
    favorite_currencies = fields.List(fields.String())


class AddFavoriteCurrencySchema(Schema):
    """Schéma pour ajouter une devise aux favoris"""

    currency_code = fields.Str(
        required=True,
        validate=lambda x: len(x) >= 3,
        error_messages={
            "required": "Le code de la devise est requis",
            "invalid": "Le code de la devise doit contenir au moins 3 caractères",
        },
    )
