SUPPORTED_CURRENCIES = {
    # Devises Fiat principales
    'USD': {'name': 'US Dollar', 'symbol': '$', 'decimal_places': 2, 'type': 'fiat'},
    'EUR': {'name': 'Euro', 'symbol': '€', 'decimal_places': 2, 'type': 'fiat'},
    'GBP': {'name': 'British Pound', 'symbol': '£', 'decimal_places': 2, 'type': 'fiat'},
    'JPY': {'name': 'Japanese Yen', 'symbol': '¥', 'decimal_places': 0, 'type': 'fiat'},
    'CHF': {'name': 'Swiss Franc', 'symbol': 'CHF', 'decimal_places': 2, 'type': 'fiat'},
    'CAD': {'name': 'Canadian Dollar', 'symbol': 'C$', 'decimal_places': 2, 'type': 'fiat'},
    'AUD': {'name': 'Australian Dollar', 'symbol': 'A$', 'decimal_places': 2, 'type': 'fiat'},
    'NZD': {'name': 'New Zealand Dollar', 'symbol': 'NZ$', 'decimal_places': 2, 'type': 'fiat'},
    
    # Autres devises importantes
    'CNY': {'name': 'Chinese Yuan', 'symbol': '¥', 'decimal_places': 2, 'type': 'fiat'},
    'INR': {'name': 'Indian Rupee', 'symbol': '₹', 'decimal_places': 2, 'type': 'fiat'},
    'KRW': {'name': 'South Korean Won', 'symbol': '₩', 'decimal_places': 0, 'type': 'fiat'},
    'SGD': {'name': 'Singapore Dollar', 'symbol': 'S$', 'decimal_places': 2, 'type': 'fiat'},
    'HKD': {'name': 'Hong Kong Dollar', 'symbol': 'HK$', 'decimal_places': 2, 'type': 'fiat'},
    'NOK': {'name': 'Norwegian Krone', 'symbol': 'kr', 'decimal_places': 2, 'type': 'fiat'},
    'SEK': {'name': 'Swedish Krona', 'symbol': 'kr', 'decimal_places': 2, 'type': 'fiat'},
    'DKK': {'name': 'Danish Krone', 'symbol': 'kr', 'decimal_places': 2, 'type': 'fiat'},
    'PLN': {'name': 'Polish Zloty', 'symbol': 'zł', 'decimal_places': 2, 'type': 'fiat'},
    'CZK': {'name': 'Czech Koruna', 'symbol': 'Kč', 'decimal_places': 2, 'type': 'fiat'},
    'HUF': {'name': 'Hungarian Forint', 'symbol': 'Ft', 'decimal_places': 0, 'type': 'fiat'},
    'RUB': {'name': 'Russian Ruble', 'symbol': '₽', 'decimal_places': 2, 'type': 'fiat'},
    'TRY': {'name': 'Turkish Lira', 'symbol': '₺', 'decimal_places': 2, 'type': 'fiat'},
    'BRL': {'name': 'Brazilian Real', 'symbol': 'R$', 'decimal_places': 2, 'type': 'fiat'},
    'MXN': {'name': 'Mexican Peso', 'symbol': '$', 'decimal_places': 2, 'type': 'fiat'},
    'ZAR': {'name': 'South African Rand', 'symbol': 'R', 'decimal_places': 2, 'type': 'fiat'},
    
    # Cryptomonnaies
    'BTC': {'name': 'Bitcoin', 'symbol': '₿', 'decimal_places': 8, 'type': 'crypto'},
    'ETH': {'name': 'Ethereum', 'symbol': 'Ξ', 'decimal_places': 8, 'type': 'crypto'},
    'LTC': {'name': 'Litecoin', 'symbol': 'Ł', 'decimal_places': 8, 'type': 'crypto'},
    'ADA': {'name': 'Cardano', 'symbol': 'ADA', 'decimal_places': 6, 'type': 'crypto'},
    'DOT': {'name': 'Polkadot', 'symbol': 'DOT', 'decimal_places': 6, 'type': 'crypto'},
}

# Paires populaires pour optimisation du cache
POPULAR_PAIRS = [
    ('USD', 'EUR'), ('EUR', 'USD'),
    ('USD', 'GBP'), ('GBP', 'USD'),
    ('USD', 'JPY'), ('JPY', 'USD'),
    ('EUR', 'GBP'), ('GBP', 'EUR'),
    ('USD', 'CHF'), ('CHF', 'USD'),
    ('USD', 'CAD'), ('CAD', 'USD'),
    ('USD', 'AUD'), ('AUD', 'USD'),
    ('USD', 'BTC'), ('BTC', 'USD'),
    ('EUR', 'BTC'), ('BTC', 'EUR'),
]