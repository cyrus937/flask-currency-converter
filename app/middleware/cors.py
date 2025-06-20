# app/middleware/cors.py
from flask_cors import CORS

# Configuration CORS
cors = CORS(
    origins=["http://localhost:3000", "http://localhost:5000"],
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)
