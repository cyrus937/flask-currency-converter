from celery import Celery
from app import create_app
from app.extensions import db
import os

def make_celery(app):
    """Crée l'instance Celery avec le contexte Flask"""
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        """Tâche avec contexte Flask"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

# Créer l'app Flask et Celery
flask_app = create_app(os.environ.get('FLASK_ENV', 'production'))
celery = make_celery(flask_app)