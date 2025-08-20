# tests/test_conversions.py
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import pytest


class TestConversions:
    """Tests pour les conversions de devises"""

    def test_convert_success(self, client):
        """Test de conversion réussie"""
        
        response = client.post('/api/conversions/convert-free', json={
            'amount': 100,
            'from_currency': 'USD',
            'to_currency': 'EUR'
        })
        
        print(response.get_json())
        assert response.status_code == 200
        data = response.get_json()
        assert data['from_currency'] == 'USD'
        assert data['to_currency'] == 'EUR'
        assert data['original_amount'] == 100.0
        assert 'converted_amount' in data
    
    def test_convert_same_currency(self, client):
        """Test de conversion vers la même devise"""
        response = client.post('/api/conversions/convert-free', json={
            'amount': 100,
            'from_currency': 'USD',
            'to_currency': 'USD'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['converted_amount'] == 100.0
        assert data['exchange_rate'] == 1.0
    
    def test_convert_invalid_amount(self, client):
        """Test de conversion avec montant invalide"""
        response = client.post('/api/conversions/convert-free', json={
            'amount': -100,
            'from_currency': 'USD',
            'to_currency': 'EUR'
        })
        
        assert response.status_code == 422
    
    def test_conversion_history_authenticated(self, client, auth_headers):
        """Test de récupération de l'historique (utilisateur authentifié)"""
        response = client.get('/api/conversions/history', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'history' in data
        assert 'count' in data

