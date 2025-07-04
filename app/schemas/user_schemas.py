# app/schemas/user_schemas.py
from marshmallow import Schema, fields, validate


class UserUpdateSchema(Schema):
    """Schéma pour la mise à jour du profil utilisateur"""
    first_name = fields.Str(validate=validate.Length(min=2, max=50))
    last_name = fields.Str(validate=validate.Length(min=2, max=50))
    preferred_currency = fields.Str(validate=validate.Length(equal=3))


class UserProfileSchema(Schema):
    """Schéma pour l'affichage du profil utilisateur"""
    id = fields.Str()
    email = fields.Email()
    first_name = fields.Str()
    last_name = fields.Str()
    full_name = fields.Str()
    is_active = fields.Bool()
    is_verified = fields.Bool()
    is_premium = fields.Bool()
    preferred_currency = fields.Str()
    created_at = fields.DateTime()
    last_login = fields.DateTime(allow_none=True)
    favorite_currencies = fields.List(fields.Str())
    active_sessions = fields.Int()

# class RegisterUserSchema(Schema):
#     """Schéma pour l'enregistrement d'un nouvel utilisateur"""
#     email = fields.Email(required=True)
#     password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))
#     first_name = fields.Str(required=True, validate=validate.Length(min=2, max=50))
#     last_name = fields.Str(required=True, validate=validate.Length(min=2, max=50))
#     preferred_currency = fields.Str(required=True, validate=validate.Length(equal=3))