# app/docs/swagger_ui.py - Configuration avancée Swagger UI
from flask import Blueprint, render_template_string

docs_bp = Blueprint('docs', __name__)

@docs_bp.route('/api-info')
def api_info():
    """Page d'information sur l'API"""
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Currency Converter API - Information</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row">
            <div class="col-md-8 mx-auto">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h3><i class="fas fa-exchange-alt"></i> Currency Converter API</h3>
                    </div>
                    <div class="card-body">
                        <h5>Documentation disponible :</h5>
                        <div class="list-group">
                            <a href="/docs" class="list-group-item list-group-item-action">
                                <strong>Swagger UI</strong> - Interface interactive
                            </a>
                            <a href="/redoc" class="list-group-item list-group-item-action">
                                <strong>ReDoc</strong> - Documentation élégante
                            </a>
                            <a href="/openapi.json" class="list-group-item list-group-item-action">
                                <strong>OpenAPI Spec</strong> - Spécification JSON
                            </a>
                        </div>
                        
                        <h5 class="mt-4">Démarrage rapide :</h5>
                        <ol>
                            <li>Créez un compte : <code>POST /api/auth/register</code></li>
                            <li>Connectez-vous : <code>POST /api/auth/login</code></li>
                            <li>Utilisez le token dans l'en-tête Authorization</li>
                            <li>Convertissez : <code>POST /api/conversions/convert</code></li>
                        </ol>
                        
                        <h5 class="mt-4">Fonctionnalités :</h5>
                        <ul>
                            <li>🔐 Authentification JWT sécurisée</li>
                            <li>💱 Conversion de 40+ devises</li>
                            <li>📊 Historique et statistiques</li>
                            <li>⭐ Gestion des favoris</li>
                            <li>🚀 Cache Redis haute performance</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    """)

# Ajouter à app/__init__.py dans register_blueprints
# app.register_blueprint(docs_bp)