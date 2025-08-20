# app/config/base.py
import os
from datetime import timedelta

class BaseConfig:
    """Configuration de base"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_TIME = 2 * 60 * 60  # 2 heures
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
    # Session Configuration
    SESSION_TIMEOUT = timedelta(days=30)
    MAX_SESSIONS_PER_USER = 15
    
    # Cache Configuration (Redis)
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
    RATELIMIT_DEFAULT = "1000 per hour"
    
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/3')
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/3')

    CURRENCYAPI_API_KEY = os.environ.get('CURRENCYAPI_API_KEY', '')
    
    # Currency Configuration
    DEFAULT_BASE_CURRENCY = 'USD'
    RATE_UPDATE_INTERVAL = 300  # 5 minutes
    RATE_CACHE_TIMEOUT = 600    # 10 minutes
    CONVERSION_FEE_RATE = 0.0  # 0%
    
    # Security
    BCRYPT_LOG_ROUNDS = 12
    
    # CORS
    CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5000", "https://localhost:5000", "*"]

    # Configuration OpenAPI/Swagger
    API_TITLE = "Currency Converter API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    OPENAPI_REDOC_PATH = "/redoc"
    OPENAPI_REDOC_URL = "https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js"

    # Description de l'API
    API_SPEC_OPTIONS = {
        'info': {
            'title': 'Currency Converter API',
            'version': 'v1',
            'description': '''
## API de Conversion de Devises avec Authentification

Cette API offre des services complets de conversion de devises en temps réel avec un système d'authentification sécurisé.

### Fonctionnalités principales :
- 🔐 **Authentification JWT** avec refresh tokens
- 💱 **Conversion de 150+ devises** (fiat et crypto)
- 📊 **Historique des conversions**
- ⭐ **Gestion des devises favorites**
- 🚀 **Cache Redis** pour performances optimales
- 📈 **Statistiques et analytics**

### Sécurité :
- Tokens JWT avec expiration
- Blacklist des tokens révoqués
- Validation des données avec Marshmallow

### Commencer :
1. Créez un compte avec `/api/auth/register`
2. Connectez-vous avec `/api/auth/login`
3. Utilisez le token dans l'en-tête `Authorization: Bearer <token>`
4. Générez une clé API avec `/api/keys/generate`
5. Ajoutez votre clé API dans l'en-tête `X-API-Key: <votre_clé_api>`
6. Convertissez des devises avec `/api/conversions/convert`
            ''',
            'contact': {
                'name': 'Support API',
                'email': os.environ.get('SUPPORT_EMAIL', '')
            },
            'license': {
                'name': 'MIT',
                'url': 'https://opensource.org/licenses/MIT'
            }
        },
        'servers': [
            {
                'url': 'http://localhost:5000',
                'description': 'Serveur de développement'
            },
            # {
            #     'url': 'https://api-currency-converter.my-finapp.com/',
            #     'description': 'Serveur de production'
            # }
        ],
        'tags': [
            {
                'name': 'Authentication',
                'description': 'Endpoints d\'authentification et gestion des comptes'
            },
            {
                'name': 'API Keys',
                'description': 'Gestion des clés API'
            },
            {
                'name': 'Conversions',
                'description': 'Conversion de devises en temps réel'
            },
            {
                'name': 'Currencies',
                'description': 'Gestion des devises et taux de change'
            },
            {
                'name': 'User',
                'description': 'Gestion du profil utilisateur'
            }
        ],
        'components': {
            'securitySchemes': {
                'bearerAuth': {
                    'type': 'http',
                    'scheme': 'bearer',
                    'bearerFormat': 'JWT',
                    'description': 'Token JWT obtenu via /api/auth/login'
                },
                'apiKeyAuth': {
                    'type': 'apiKey',
                    'in': 'header',
                    'name': 'X-API-Key',
                    'description': 'Clé API pour accéder aux fonctionnalités avancées'
                }
            }
        },
        'security': [
            {
                'bearerAuth': []
            }
        ]
    }