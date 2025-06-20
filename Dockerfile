FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier les requirements
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

# Copier le code
COPY . .

# Variables d'environnement
ENV PYTHONPATH=/app
ENV FLASK_APP=run.py

# Exposer le port
EXPOSE 5000

# Commande par défaut
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "wsgi:app"]