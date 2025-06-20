# app/utils/helpers.py
from decimal import Decimal
from datetime import datetime
import re
from babel.numbers import format_currency as babel_format_currency
from babel.dates import format_datetime as babel_format_datetime


def format_currency(amount, currency_code, locale='en_US'):
    """Formate un montant avec la devise"""
    try:
        return babel_format_currency(amount, currency_code, locale=locale)
    except Exception:
        return f"{amount:.2f} {currency_code}"


def format_datetime(dt, locale='en_US', format='medium'):
    """Formate une date/heure"""
    try:
        return babel_format_datetime(dt, format=format, locale=locale)
    except Exception:
        return dt.strftime('%Y-%m-%d %H:%M:%S')


def round_currency(amount, decimal_places=2):
    """Arrondit un montant selon les décimales de la devise"""
    if isinstance(amount, str):
        amount = Decimal(amount)
    elif not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    
    format_str = f"0.{'0' * decimal_places}"
    return amount.quantize(Decimal(format_str))


def get_currency_symbol(currency_code):
    """Retourne le symbole d'une devise"""
    symbols = {
        'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥',
        'CHF': 'CHF', 'CAD': 'C$', 'AUD': 'A$', 'CNY': '¥',
        'BTC': '₿', 'ETH': 'Ξ'
    }
    return symbols.get(currency_code, currency_code)


def sanitize_user_agent(user_agent):
    """Nettoie et limite la taille du user agent"""
    if not user_agent:
        return None
    
    # Supprimer les caractères potentiellement dangereux
    cleaned = re.sub(r'[<>"\']', '', user_agent)
    
    # Limiter la taille
    return cleaned[:500] if len(cleaned) > 500 else cleaned