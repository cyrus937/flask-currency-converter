from tasks.celery_app import celery
from app.services.rate_fetcher_service import RateFetcherService
from app.models.exchange_rate import ExchangeRate
from app.config.currencies import POPULAR_PAIRS
from app.extensions import db


@celery.task
def update_exchange_rates():
    """Met à jour les taux de change toutes les 5 minutes"""
    print("Mise à jour des taux de change...")
    
    rate_fetcher = RateFetcherService()
    updated_count = 0
    error_count = 0
    
    for from_currency, to_currency in POPULAR_PAIRS:
        try:
            rate = rate_fetcher.fetch_rate(from_currency, to_currency)
            provider = rate_fetcher.last_successful_provider
            
            ExchangeRate.update_or_create(from_currency, to_currency, rate, provider)
            updated_count += 1
            
        except Exception as e:
            print(f"Erreur pour {from_currency}/{to_currency}: {e}")
            error_count += 1
    
    print(f"Mise à jour terminée. {updated_count} taux mis à jour, {error_count} erreurs")
    return {'updated': updated_count, 'errors': error_count}


@celery.task
def cleanup_old_data():
    """Nettoie les données anciennes"""
    print("Nettoyage des données anciennes...")
    
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
    # Mise à jour des taux toutes les 5 minutes
    'update-rates': {
        'task': 'tasks.rate_updater.update_exchange_rates',
        'schedule': 300.0,  # 5 minutes
    },
    
    # Nettoyage quotidien à 2h du matin
    'cleanup-old-data': {
        'task': 'tasks.rate_updater.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),
    },
}

celery.conf.timezone = 'UTC'