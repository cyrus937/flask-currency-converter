import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from tasks.celery_app import celery
from app.models.exchange_rate import ExchangeRate

@celery.task
def fetch_all_exchange_rates():
    """Récupère tous les taux de change"""
    from app.providers.currencyapi_provider import CurrencyAPIProvider
    rate_fetcher = CurrencyAPIProvider()
    rate_fetcher.fetch_exchange_rates()
    return {'status': 'completed'}


@celery.task
def cleanup_old_data():
    """Nettoie les données anciennes"""
    
    from app.models.session import Session
    from app.models.refresh_token import RefreshToken
    
    # Nettoyer les sessions expirées
    expired_sessions = Session.cleanup_expired_sessions()
    
    # Nettoyer les refresh tokens expirés
    expired_tokens = RefreshToken.cleanup_expired_tokens()
    
    # Nettoyer les anciens taux (> 1 an)
    old_rates = ExchangeRate.cleanup_old_rates(days=365)
    
    print(f"Nettoyage terminé: {expired_sessions} sessions, {expired_tokens} tokens, {old_rates} taux")
    return {
        'expired_sessions': expired_sessions,
        'expired_tokens': expired_tokens,
        'old_rates': old_rates
    }


# Configuration Celery Beat pour les tâches périodiques
from celery.schedules import crontab
celery.conf.beat_schedule = {
    
    # Nettoyage quotidien à 2h du matin
    'cleanup-old-data': {
        'task': 'tasks.rate_updater.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),
    },
    
    # Récupération de tous les taux toutes les 2.5 heures
    'fetch-all-exchange-rates': {
        'task': 'tasks.rate_updater.fetch_all_exchange_rates',
        'schedule': 9000,  # Toutes les 2.5 heures
    },
}

celery.conf.timezone = 'UTC'

# Import nécessaire pour l'enregistrement des tâches
