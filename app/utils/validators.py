# app/utils/validators.py
import re
from decimal import Decimal, InvalidOperation
from app.utils.exceptions import ValidationError


def validate_currency_code(code):
    """Valide un code de devise"""
    if not code or len(code) != 3:
        raise ValidationError("Le code de devise doit contenir exactement 3 caractères")
    
    if not code.isupper():
        raise ValidationError("Le code de devise doit être en majuscules")
    
    if not re.match(r'^[A-Z]{3}$', code):
        raise ValidationError("Le code de devise doit contenir uniquement des lettres")
    
    return True


def validate_amount(amount):
    """Valide un montant de conversion"""
    try:
        amount = Decimal(str(amount))
        
        if amount <= 0:
            raise ValidationError("Le montant doit être positif")
        
        if amount > Decimal('1000000000'):
            raise ValidationError("Le montant est trop élevé")
        
        return amount
        
    except (InvalidOperation, ValueError):
        raise ValidationError("Le montant doit être un nombre valide")


def validate_email(email):
    """Valide un email"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not email or not re.match(email_regex, email):
        raise ValidationError("Adresse email invalide")
    
    return True
