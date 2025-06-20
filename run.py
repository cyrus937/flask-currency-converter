# run.py - Point d'entrée pour le développement
from app import create_app
from app.extensions import db
from app.models import *  # Import tous les modèles
import os

app = create_app(os.environ.get('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    """Contexte pour Flask shell"""
    return {
        'db': db,
        'User': User,
        'Session': Session,
        'RefreshToken': RefreshToken,
        'Currency': Currency,
        'ExchangeRate': ExchangeRate,
        'Conversion': Conversion,
        'UserFavoriteCurrency': UserFavoriteCurrency
    }

@app.cli.command()
def create_tables():
    """Crée toutes les tables de la base de données"""
    db.create_all()
    print("Tables créées avec succès!")

@app.cli.command()
def populate_currencies():
    """Peuple la base avec les devises de base"""
    from scripts.populate_currencies import populate_default_currencies
    populate_default_currencies()
    print("Devises ajoutées avec succès!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
