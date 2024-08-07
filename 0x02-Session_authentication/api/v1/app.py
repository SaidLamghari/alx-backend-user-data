#!/usr/bin/env python3
"""Module de routage pour l'API.
"""

from api.v1.views import app_views
from api.v1.auth.auth import Auth
from api.v1.auth.basic_auth import BasicAuth

import os
from os import getenv
from flask import Flask
from flask import jsonify
from flask import abort
from flask import request
from flask_cors import (CORS, cross_origin)


# Création de l'application Flask
app = Flask(__name__)

# Enregistrement du blueprint des vues de l'API
app.register_blueprint(app_views)

# Configuration de CORS (Cross-Origin Resource Sharing) pour
# permettre les requêtes de n'importe quelle origine
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

# Initialisation de la variable d'authentification
auth = None

# Détermination du type d'authentification à
# utiliser à partir des variables d'environnement
authtpe = getenv('AUTH_TYPE', 'auth')
if authtpe == 'auth':
    auth = Auth()
elif authtpe == 'basic_auth':
    auth = BasicAuth()


# Gestionnaire d'erreur 404 - Ressource non trouvée
@app.errorhandler(404)
def not_found(error) -> str:
    """Gestionnaire pour les
    erreurs 404 - Ressource non trouvée.
    """
    return jsonify({"error": "Not found"}), 404


# Gestionnaire d'erreur 401 - Non autorisé
@app.errorhandler(401)
def unauthorizedhandler(error) -> str:
    """Gestionnaire pour les erreurs 401 - Non autorisé.
    """
    return jsonify({"error": "Unauthorized"}), 401


# Gestionnaire d'erreur 403 - Interdit
@app.errorhandler(403)
def forbiddenhandler(error) -> str:
    """Gestionnaire pour les erreurs 403 - Interdit.
    """
    return jsonify({"error": "Forbidden"}), 403


# Fonction appelée avant le traitement de chaque requête
@app.before_request
def authenticate_before_request():
    """Authentifie un utilisateur
    avant le traitement d'une requête.
    """
    if auth:
        # Liste des chemins d'URL exclus de l'authentification
        chemins_exclus = ['/api/v1/status/',
                          '/api/v1/unauthorized/', '/api/v1/forbidden/',
                          ]
        # Vérifie si le chemin de la requête
        # nécessite une authentification
        if auth.require_auth(request.path, chemins_exclus):
            # Récupère l'en-tête d'autorisation de la requête
            en_tete = auth.authorization_header(request)
            # Récupère l'utilisateur actuel basé sur la requête
            utilisateur = auth.current_user(request)
            # Si l'en-tête d'autorisation est
            # manquant, retourne une erreur 401
            if en_tete is None:
                abort(401)
            # Si l'utilisateur est non identifié,
            # retourne une erreur 403
            if utilisateur is None:
                abort(403)


# Exécution de l'application Flask
if __name__ == "__main__":
    # Récupération de l'hôte et du port depuis les variables
    # d'environnement, avec des valeurs par défaut
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    # Lancement de l'application sur l'hôte et le port spécifiés
    app.run(host=host, port=port)
