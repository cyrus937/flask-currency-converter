# tests/test_currencies.py
class TestCurrencies:
    """Tests pour les devises"""
    
    def test_get_currencies(self, client):
        """Test de récupération des devises"""
        response = client.get('/api/currencies')
        assert response.status_code == 200
        data = response.get_json()
        assert 'currencies' in data
        assert len(data['currencies']) > 0
    
    def test_get_popular_currencies(self, client):
        """Test de récupération des devises populaires"""
        response = client.get('/api/currencies/popular')
        assert response.status_code == 200
        data = response.get_json()
        assert 'currencies' in data
    
    def test_add_favorite_currency(self, client, auth_headers):
        """Test d'ajout d'une devise aux favoris"""
        response = client.post('/api/currencies/favorites', 
                              json={'currency_code': 'EUR'}, 
                              headers=auth_headers)
        assert response.status_code == 200
    
    def test_get_favorite_currencies(self, client, auth_headers):
        """Test de récupération des devises favorites"""
        response = client.get('/api/currencies/favorites', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'favorite_currencies' in data
