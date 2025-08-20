# tests/conftest.py
from decimal import Decimal
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import pytest
import tempfile
import os
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.currency import Currency
from app.models.exchange_rate import ExchangeRate


@pytest.fixture
def app():
    """Crée une instance de l'app pour les tests"""
    # Base de données temporaire
    db_fd, db_path = tempfile.mkstemp()
    
    # Configuration de test
    config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'CACHE_TYPE': 'simple',
        'JWT_SECRET_KEY': 'test-secret',
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False
    }
    
    app = create_app('testing')
    app.config.update(config)
    
    with app.app_context():
        db.create_all()
        # Ajouter quelques devises de test
        currencies = [
            Currency(code='USD', name='US Dollar', symbol='$'),
            Currency(code='EUR', name='Euro', symbol='€'),
            Currency(code='GBP', name='British Pound', symbol='£'),
        ]
        for currency in currencies:
            currency.save()
        
        
        exchange_rates = [
            ExchangeRate(from_currency='USD', to_currency='EUR', rate=Decimal('0.85'), provider='test_provider'),
            ExchangeRate(from_currency='USD', to_currency='USD', rate=Decimal('1.00'), provider='test_provider'),
            ExchangeRate(from_currency='EUR', to_currency='USD', rate=Decimal('1.15'), provider='test_provider'),
            ExchangeRate(from_currency='GBP', to_currency='USD', rate=Decimal('1.30'), provider='test_provider'),
        ]
        
        for rate in exchange_rates:
            rate.save()

        yield app
        
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Client de test Flask"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Runner CLI de test"""
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    """Utilisateur de test"""
    with app.app_context():
        user = User.create_user(
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        return user


@pytest.fixture
def auth_headers(client, test_user):
    """Headers d'authentification pour les tests"""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    data = response.get_json()
    access_token = data['access_token']
    
    return {'Authorization': f'Bearer {access_token}'}
