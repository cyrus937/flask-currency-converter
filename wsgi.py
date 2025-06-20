# wsgi.py - Point d'entrée pour la production
from app import create_app
import os

app = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == "__main__":
    app.run()