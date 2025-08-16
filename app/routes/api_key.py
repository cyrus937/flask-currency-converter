from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request

from app.models.api_key import ApiKey
from app.schemas.api_key_schemas import ApiKeyCreateSchema, ApiKeySchema
from app.schemas.response_schemas import MessageSchema

api_keys_bp = Blueprint(
    'api_keys', 
    __name__, 
    url_prefix='/api/keys',
    description='Gestion des clés API'
)

@api_keys_bp.route('/generate', methods=['POST'])
@api_keys_bp.arguments(ApiKeyCreateSchema, location='json', content_type='application/json')
@api_keys_bp.response(201, ApiKeySchema)
@api_keys_bp.doc(
    summary="Créer une nouvelle clé API",
    description="Créer une nouvelle clé API",
    tags=["API Keys"],
    security=[{"bearerAuth": []}]
)
@jwt_required()
def create_api_key():
    try:
        user_id = get_jwt_identity()
    except Exception as e:
        abort(401, message="Token invalide ou expiré.")
    data = request.get_json()
    name = data.get('name')
    if not name:
        abort(400, message="Le nom de la clé API est requis.")
    user_id = request.user_id
    api_key, key = ApiKey.create_api_key(name, user_id)
    return {"id": api_key.id, "name": api_key.name, "key": key}

@api_keys_bp.route('/deactivate', methods=['POST'])
@api_keys_bp.arguments(schema={'type': 'object', 'properties': {'key': {'type': 'string'}}}, location='json')
@api_keys_bp.response(200, MessageSchema)
@api_keys_bp.doc(
    summary="Désactiver une clé API",
    description="Désactiver une clé API",
    tags=["API Keys"],
    security=[{"bearerAuth": []}]
)
@jwt_required()
def deactivate_api_key(args):
    try:
        user_id = get_jwt_identity()
    except Exception as e:
        abort(401, message="Token invalide ou expiré.")
    
    api_key: ApiKey = ApiKey.find_by_key(args.get('key', ""))
    if not api_key:
        abort(404, message="Clé API non trouvée.")
    api_key.deactivate()
    
    return {"message": "Clé API désactivée avec succès."}

@api_keys_bp.route('/<string:api_key_id>', methods=['DELETE'])
@api_keys_bp.response(200, MessageSchema)
@api_keys_bp.doc(
    summary="Supprimer une clé API",
    description="Supprimer une clé API",
    tags=["API Keys"],
    security=[{"bearerAuth": []}]
)
@jwt_required()
def delete_api_key(api_key_id):
    try:
        user_id = get_jwt_identity()
    except Exception as e:
        abort(401, message="Token invalide ou expiré.")
    ApiKey.delete_api_key(api_key_id, user_id)
    return {"message": "Clé API supprimée avec succès."}