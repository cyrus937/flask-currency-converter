import sys
import os

# Ajouter le répertoire parent au Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app import create_app
from app.extensions import db
from app.models.currency import Currency
from app.config.currencies import SUPPORTED_CURRENCIES


def populate_default_currencies():
    """Peuple la base de données avec les devises par défaut"""
    
    print("=" * 50)
    print("POPULATION DES DEVISES")
    print("=" * 50)
    
    try:
        app = create_app(os.environ.get('FLASK_ENV', 'development'))
        
        with app.app_context():
            print(f"Connexion à la base de données: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Non définie')}")
            print(f"Ajout de {len(SUPPORTED_CURRENCIES)} devises...")
            print("-" * 50)
            
            added_count = 0
            updated_count = 0
            
            for code, info in SUPPORTED_CURRENCIES.items():
                try:
                    # Vérifier si la devise existe déjà
                    existing = Currency.query.filter_by(code=code).first()
                    
                    if not existing:
                        currency = Currency(
                            code=code,
                            name=info['name'],
                            symbol=info['symbol'],
                            decimal_places=info['decimal_places'],
                            is_crypto=(info['type'] == 'crypto'),
                            country_code=info.get('country_code')
                        )
                        db.session.add(currency)
                        print(f"✅ Ajouté: {code} - {info['name']}")
                        added_count += 1
                    else:
                        # Mettre à jour les informations si nécessaire
                        existing.name = info['name']
                        existing.symbol = info['symbol']
                        existing.decimal_places = info['decimal_places']
                        existing.is_crypto = (info['type'] == 'crypto')
                        existing.country_code = info.get('country_code')
                        print(f"🔄 Mis à jour: {code} - {info['name']}")
                        updated_count += 1
                        
                except Exception as e:
                    print(f"❌ Erreur pour {code}: {str(e)}")
                    continue
            
            # Commit toutes les modifications
            db.session.commit()
            
            print("-" * 50)
            print(f"✅ TERMINÉ!")
            print(f"📊 Statistiques:")
            print(f"   - Devises ajoutées: {added_count}")
            print(f"   - Devises mises à jour: {updated_count}")
            print(f"   - Total dans la base: {Currency.query.count()}")
            print(f"   - Devises actives: {Currency.query.filter_by(is_active=True).count()}")
            print(f"   - Cryptomonnaies: {Currency.query.filter_by(is_crypto=True).count()}")
            
            # Afficher quelques exemples
            print(f"\n🎯 Exemples de devises disponibles:")
            examples = Currency.query.limit(5).all()
            for curr in examples:
                crypto_label = " (CRYPTO)" if curr.is_crypto else ""
                print(f"   - {curr.code}: {curr.name} ({curr.symbol}){crypto_label}")
            
            print("\n🚀 Vous pouvez maintenant utiliser le convertisseur!")
            
    except Exception as e:
        print(f"❌ ERREUR FATALE: {str(e)}")
        print("Vérifiez votre configuration de base de données dans .env")
        sys.exit(1)


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
        populate_default_currencies()
    else:
        print("❌ Problème d'environnement détecté. Arrêt du script.")
        sys.exit(1)