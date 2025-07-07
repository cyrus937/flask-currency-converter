# tests/test_auth.py
import sys
import os

# Ajouter le répertoire parent au Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import pytest
from app.models.user import User


class TestAuth:
    """Tests pour l'authentification"""
    
    def test_register_success(self, client):
        """Test d'enregistrement réussi"""
        response = client.post('/api/auth/register', json={
            'email': 'newuser@example.com',
            'password': 'password123',
            'first_name': 'New',
            'last_name': 'User'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Utilisateur créé avec succès'
        assert data['user']['email'] == 'newuser@example.com'
    
    def test_register_duplicate_email(self, client, test_user):
        """Test d'enregistrement avec email existant"""
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'User'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'existe déjà' in data['error']
    
    def test_login_success(self, client, test_user):
        """Test de connexion réussie"""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['email'] == 'test@example.com'
    
    def test_login_invalid_credentials(self, client, test_user):
        """Test de connexion avec mauvais identifiants"""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'incorrect' in data['error']
    
    def test_protected_route_without_token(self, client):
        """Test d'accès à une route protégée sans token"""
        response = client.get('/api/auth/profile')
        assert response.status_code == 401
    
    def test_protected_route_with_token(self, client, auth_headers):
        """Test d'accès à une route protégée avec token"""
        response = client.get('/api/auth/profile', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['email'] == 'test@example.com'
