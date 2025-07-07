from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_mail import Mail
from flask_migrate import Migrate

from flask_smorest import Api

# Initialisation des extensions
db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
cache = Cache()
cors = CORS(
    origins=["http://localhost:3000", "http://localhost:5000", "*"],
    allow_headers=["Content-Type", "Authorization", "*"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    supports_credentials=True,
)
mail = Mail()
migrate = Migrate()
api = Api()