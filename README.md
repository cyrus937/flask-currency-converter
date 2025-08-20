# flask-currency-converter-

# Flask Currency Converter with Authentication

Une application Flask complète combinant un système d'authentification robuste et un convertisseur de devises en temps réel.

## 🚀 Fonctionnalités

### Authentification
- ✅ Inscription/Connexion avec JWT
- ✅ Gestion des sessions multi-appareils
- ✅ Refresh tokens avec rotation automatique
- ✅ Rate limiting et sécurité renforcée
- ✅ Gestion des mots de passe avec bcrypt

### Conversion de Devises
- ✅ Conversion en temps réel (30+ devises)
- ✅ Providers multiples avec fallback (Currency api actuellement supporté)
- ✅ Cache Redis pour performances optimales
- ✅ Historique des conversions
- ✅ Devises favorites par utilisateur
- ✅ Support des cryptomonnaies

### Dashboard
- ✅ Interface web moderne avec Bootstrap
- ✅ Statistiques utilisateur
- ✅ Conversion rapide
- ✅ Gestion des favoris

## 🛠️ Technologies

- **Backend**: Flask, SQLAlchemy, Redis
- **Authentification**: Flask-JWT-Extended
- **Base de données**: PostgreSQL/SQLite
- **Cache**: Redis
- **Tâches**: Celery + Redis
- **Tests**: Pytest
- **Déploiement**: Docker, Gunicorn

## 📦 Installation

### Prérequis
- Python 3.11+
- PostgreSQL (ou SQLite pour dev)
- Redis

### Installation manuelle

```bash
# 1. Cloner le projet
git clone <repository>
cd flask-auth-currency

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements/development.txt

# 4. Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos configurations

# 5. Initialiser la base de données
## Migration base de données
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

python scripts/populate_currencies.py

# 6. Créer un utilisateur admin (optionnel)
python scripts/create_admin.py

# 7. Lancer l'application
python run.py
```

### Avec Docker

```bash
# Lancer tous les services
docker-compose up -d

# Initialiser la base
docker-compose exec web flask db upgrade
docker-compose exec web python scripts/populate_currencies.py
```

Ou utiliser le fichier manage_docker.sh

```bash
# Afficher la liste des commande possible
./manage_docker.sh help

# Installation complète
./manage_docker.sh setup
```

## ⚙️ Configuration

### Variables d'environnement (.env)

```env
# Flask
SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# Base de données
DATABASE_URL=postgresql://user:pass@localhost/db_name

# Redis
REDIS_URL=redis://localhost:6379/0

# APIs externes (optionnel)
CURRENCYAPI_API_KEY=your-currency-api-key

# Support Email
SUPPORT_EMAIL=test-support@currencyconverter.com

# Email (optionnel)
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## 🔌 API Endpoints

### Authentification
```
POST /api/auth/register      # Inscription
POST /api/auth/login         # Connexion
POST /api/auth/refresh       # Rafraîchir token
POST /api/auth/logout        # Déconnexion
GET  /api/auth/profile       # Profil utilisateur
```

### Conversions
```
POST /api/conversions/convert    # Convertir devises
GET  /api/conversions/history    # Historique utilisateur
POST /api/conversions/batch      # Conversion en lot
```

### Devises
```
GET  /api/currencies             # Liste des devises
GET  /api/currencies/popular     # Devises populaires
POST /api/currencies/favorites   # Ajouter favori
GET  /api/currencies/rates       # Taux actuels
```

## 📖 Accès à la Documentation
Une fois l'application lancée, vous avez accès à :

- 📊 Swagger UI Interactive : http://localhost:5000/docs
- 📚 ReDoc (Documentation élégante) : http://localhost:5000/redoc
- 📄 Spécification OpenAPI : http://localhost:5000/openapi.json

### ✨ Fonctionnalités Swagger
Documentation Complète :

* ✅ 50+ endpoints documentés avec exemples
* ✅ Authentification JWT intégrée dans l'interface
* ✅ Schémas de validation automatiques
* ✅ Test direct des APIs depuis le navigateur
* ✅ Codes d'erreur documentés
* ✅ Groupement par catégories (Auth, Conversions, Currencies, User)

## 📊 Exemples d'utilisation

### Conversion simple
```bash
curl -X POST http://localhost:5000/api/conversions/convert-free \
  -H "Content-Type: application/json" \
  -d '{"amount": 100, "from_currency": "USD", "to_currency": "EUR"}'
```

### Authentification
```bash
# Connexion
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Utiliser le token
curl -X GET http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer <access_token>"
```

## 🧪 Tests

```bash
# Lancer tous les tests
pytest --disable-warnings

# Tests avec couverture
pytest --disable-warnings --cov=app tests/

# Tests spécifiques
pytest --disable-warnings tests/test_auth.py
pytest --disable-warnings tests/test_conversions.py
```

## 🔧 Déploiement

### Production avec Docker

```bash
# 1. Construire l'image
docker build -t currency-converter .

# 2. Variables d'environnement production
cp .env.example .env.prod
# Configurer pour la production

# 3. Lancer avec docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### Avec Gunicorn

```bash
# Installation
pip install -r requirements/production.txt

# Lancement
gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app
```

## 📈 Monitoring

### Tâches Celery

```bash
# Worker
celery -A tasks.celery_app worker --loglevel=info

# Scheduler (tâches périodiques)
celery -A tasks.celery_app beat --loglevel=info

# Monitor
celery -A tasks.celery_app flower
```

### Logs et métriques

- Les logs sont configurés via la variable `LOG_LEVEL`
- Intégration Sentry pour la production
- Métriques Redis disponibles via CLI

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit (`git commit -am 'Ajouter nouvelle fonctionnalité'`)
4. Push (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## 📝 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

- **Issues**: Ouvrir une issue sur GitHub
- **Documentation**: Voir `/docs` pour plus de détails
- **API**: Documentation interactive à `/docs/api` (en développement)

## 🔮 Roadmap

- [ ] Interface React/Vue.js
- [ ] Support WebSocket pour taux temps réel
- [ ] API GraphQL
- [ ] Notifications par email/SMS
- [ ] Dashboard analytics avancé
- [ ] Support plus de cryptomonnaies
- [ ] API mobile (React Native/Flutter)

---

Made with ❤️ using Flask