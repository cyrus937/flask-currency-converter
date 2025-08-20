from marshmallow import Schema, fields, validate

class ApiKeySchema(Schema):
    id = fields.String(required=True)
    name = fields.String(required=True, validate=validate.Length(min=2, max=150))
    key = fields.String(required=True)

class ApiKeyListSchema(Schema):
    items = fields.List(fields.Nested(ApiKeySchema))
    total = fields.Integer(required=True)
    
class ApiKeyCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=150))
    