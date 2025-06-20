from ..app import create_app
from ..app.extensions import db
from ..app.models.currency import Currency
from ..app.config.currencies import SUPPORTED_CURRENCIES


def populate_default_currencies():
    """Peuple la base de données avec les devises par défaut"""
    
    app = create_app()
    
    with app.app_context():
        print("Ajout des devises...")
        
        for code, info in SUPPORTED_CURRENCIES.items():
            # Vérifier si la devise existe déjà
            existing = Currency.find_by_code(code)
            
            if not existing:
                currency = Currency(
                    code=code,
                    name=info['name'],
                    symbol=info['symbol'],
                    decimal_places=info['decimal_places'],
                    is_crypto=(info['type'] == 'crypto')
                )
                currency.save()
                print(f"Ajouté: {code} - {info['name']}")
            else:
                print(f"Existe déjà: {code}")
        
        print(f"Terminé! {len(SUPPORTED_CURRENCIES)} devises traitées.")