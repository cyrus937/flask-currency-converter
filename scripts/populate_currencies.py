import sys
import os

# Ajouter le répertoire parent au Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import app
from app import create_app


def check_environment():
    """Vérifie l'environnement avant l'exécution"""
    print("🔍 Vérification de l'environnement...")
    
    # Vérifier les variables d'environnement importantes
    required_vars = ['DATABASE_URL']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Variables d'environnement manquantes: {', '.join(missing_vars)}")
        print("Assurez-vous que votre fichier .env est configuré correctement.")
    
    # Vérifier que les modules sont importables
    try:
        from app.models.currency import Currency
        print("✅ Modules importés avec succès")
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    
    return True


if __name__ == '__main__':
    print("🚀 Démarrage du script de population des devises...")
    
    if check_environment():
        app = create_app(os.environ.get('FLASK_ENV', 'development'))
        with app.app_context():
            print("✅ Environnement vérifié. Lancement de la population des devises...")
            # populate_default_currencies()
            from app.providers.currencyapi_provider import CurrencyAPIProvider
            provider = CurrencyAPIProvider()
            print("🔄 Récupération des devises depuis le provider...")
            provider.fetch_currencies()
            print("✅ Devises récupérées avec succès.")
        # populate_default_currencies()
        # print("✅ Environnement vérifié avec succès. Vous pouvez lancer le script.")
    else:
        print("❌ Problème d'environnement détecté. Arrêt du script.")
        sys.exit(1)