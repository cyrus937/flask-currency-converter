import sys
import os

# Ajouter le répertoire parent au Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app import create_app
from app.extensions import db
from app.models.session import Session
from app.models.refresh_token import RefreshToken
from app.models.exchange_rate import ExchangeRate
from datetime import datetime, timedelta


def cleanup_old_data():
    """Nettoie les données anciennes de la base"""
    
    app = create_app()
    
    with app.app_context():
        print("Nettoyage des données anciennes...")
        print("-" * 40)
        
        # Nettoyer les sessions expirées
        expired_sessions = Session.cleanup_expired_sessions()
        print(f"Sessions expirées supprimées: {expired_sessions}")
        
        # Nettoyer les refresh tokens expirés
        expired_tokens = RefreshToken.cleanup_expired_tokens()
        print(f"Refresh tokens expirés supprimés: {expired_tokens}")
        
        # Nettoyer les anciens taux de change (> 1 an)
        old_rates = ExchangeRate.cleanup_old_rates(days=365)
        print(f"Anciens taux de change supprimés: {old_rates}")
        
        print("\nNettoyage terminé!")


if __name__ == '__main__':
    cleanup_old_data()