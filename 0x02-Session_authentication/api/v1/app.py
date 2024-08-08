#!/usr/bin/env python3
"""Module de routage pour l'API.
"""
import os

from os import getenv

from flask_cors import (CORS, cross_origin)
from flask import Flask, jsonify, abort, request

from api.v1.views import app_views
from api.v1.auth.session_db_auth import SessionDBAuth
from api.v1.auth.auth import Auth
from api.v1.auth.session_auth import SessionAuth

from api.v1.auth.session_exp_auth import SessionExpAuth

from api.v1.auth.basic_auth import BasicAuth


app = Flask(__name__)
# Enregistre les routes définies dans app_views (dans le module api.v1.views)
app.register_blueprint(app_views)

# Configure CORS pour permettre les requêtes de toutes les origines sur les routes API
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

# Initialise l'objet d'authentification basé sur le type d'authentification spécifié
auth = None
 # Obtient le type d'authentification
 # depuis les variables d'environnement
auth_type = getenv('AUTH_TYPE', 'auth')
if auth_type == 'auth':
    auth = Auth()
elif auth_type == 'basic_auth':
    auth = BasicAuth()
elif auth_type == 'session_auth':
    auth = SessionAuth()
elif auth_type == 'session_exp_auth':
    auth = SessionExpAuth()
elif auth_type == 'session_db_auth':
    auth = SessionDBAuth()


@app.errorhandler(404)
def not_found(error) -> str:
    """
    Gestionnaire pour les erreurs 404 (Non trouvé).
    
    Args:
        error: L'erreur qui a été levée.
    
    Returns:
        str: Réponse JSON avec un message d'erreur 404.
    """
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(401)
def unauthorized(error) -> str:
    """Gestionnaire pour les erreurs 401 (Non autorisé).
    
    Args:
        error: L'erreur qui a été levée.
    
    Returns:
        str: Réponse JSON avec un message d'erreur 401.
    """
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def forbidden(error) -> str:
    """Gestionnaire pour les erreurs 403 (Interdit).
    
    Args:
        error: L'erreur qui a été levée.
    
    Returns:
        str: Réponse JSON avec un message d'erreur 403.
    """
    return jsonify({"error": "Forbidden"}), 403


@app.before_request
def authenticate_user():
    """Authentifie un utilisateur avant de traiter une requête.
    
    Vérifie si une authentification est requise pour la route demandée.
    Si l'utilisateur n'est pas authentifié
    correctement, il renvoie une erreur 401 ou 403.
    """
    if auth:
        # Définir les chemins exclus de l'authentification
        excluded_paths = [
            "/api/v1/status/",
            "/api/v1/unauthorized/",
            "/api/v1/forbidden/",
            "/api/v1/auth_session/login/",
        ]
        # Vérifie si l'authentification est requise pour la route demandée
        if auth.require_auth(request.path, excluded_paths):
            user = auth.current_user(request)
            # Vérifie si l'en-tête d'autorisation
            # et le cookie de session sont présents
            # Renvoie une erreur 401 si aucune
            # authentification n'est trouvée
            if auth.authorization_header(request) is None and \
                    auth.session_cookie(request) is None:
                abort(401)
            # Renvoie une erreur 403 si l'utilisateur n'est pas autorisé
            if user is None:
                abort(403)
            # Ajoute l'utilisateur courant à la requête
            request.current_user = user


if __name__ == "__main__":
    # Obtient les informations de configuration pour l'hôte
    # et le port depuis les variables d'environnement
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    # Démarre l'application Flask
    app.run(host=host, port=port)
