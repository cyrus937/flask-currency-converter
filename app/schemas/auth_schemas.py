# app/schemas/auth_schemas.py
from marshmallow import Schema, fields, validate, validates 
import re

from app.utils.exceptions import ValidationError


class RegisterSchema(Schema):
    """Schéma pour l'enregistrement utilisateur"""
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128))
    first_name = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    preferred_currency = fields.Str(missing='USD', validate=validate.Length(equal=3))
    
    @validates('password')
    def validate_password(self, value):
        """Valide la complexité du mot de passe"""
        if not re.search(r'[A-Za-z]', value):
            raise ValidationError('Le mot de passe doit contenir au moins une lettre')
        if not re.search(r'\d', value):
            raise ValidationError('Le mot de passe doit contenir au moins un chiffre')
    
    @validates('preferred_currency')
    def validate_currency(self, value):
        """Valide le code de devise"""
        if value and not value.isupper():
            raise ValidationError('Le code de devise doit être en majuscules')


class LoginSchema(Schema):
    """Schéma pour la connexion"""
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class RefreshTokenSchema(Schema):
    """Schéma pour le rafraîchissement de token"""
    refresh_token = fields.Str(required=True)


class ChangePasswordSchema(Schema):
    """Schéma pour le changement de mot de passe"""
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8, max=128))
    
    @validates('new_password')
    def validate_new_password(self, value):
        """Valide la complexité du nouveau mot de passe"""
        if not re.search(r'[A-Za-z]', value):
            raise ValidationError('Le mot de passe doit contenir au moins une lettre')
        if not re.search(r'\d', value):
            raise ValidationError('Le mot de passe doit contenir au moins un chiffre')
