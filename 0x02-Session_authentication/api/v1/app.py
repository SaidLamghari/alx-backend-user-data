#!/usr/bin/env python3
"""
Module de routage pour l'API.
"""

import os
from os import getenv
from typing import Tuple

from flask import Flask, abort, jsonify, request
from flask_cors import CORS

from api.v1.auth.auth import Auth
from api.v1.auth.basic_auth import BasicAuth
from api.v1.auth.session_auth import SessionAuth
from api.v1.auth.session_db_auth import SessionDBAuth
from api.v1.auth.session_exp_auth import SessionExpAuth
from api.v1.views import app_views

# Création de l'application Flask
app = Flask(__name__)

# Enregistrement des routes définies dans app_views
app.register_blueprint(app_views)

# Configuration des politiques CORS (Cross-Origin Resource Sharing)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

# Création d'une variable auth initialisée à None après la définition de CORS
auth = None

# Détermination du type d'authentification à utiliser en fonction de la variable d'environnement AUTH_TYPE
# AUTH_TYPE est lu depuis les variables d'environnement, avec une valeur par défaut 'default'
auth_type = getenv('AUTH_TYPE', 'default')

if auth_type == "session_auth":
    # Si AUTH_TYPE est égal à 'session_auth', instancier SessionAuth
    auth = SessionAuth()
elif auth_type == 'session_exp_auth':
    # Si AUTH_TYPE est égal à 'session_exp_auth', instancier SessionExpAuth
    auth = SessionExpAuth()
elif auth_type == 'session_db_auth':
    # Si AUTH_TYPE est égal à 'session_db_auth', instancier SessionDBAuth
    auth = SessionDBAuth()
elif auth_type == "basic_auth":
    # Si AUTH_TYPE est égal à 'basic_auth', instancier BasicAuth
    auth = BasicAuth()
else:
    # Sinon, utiliser l'authentification par défaut (Auth)
    auth = Auth()


@app.errorhandler(404)
def not_found(error) -> str:
    """Gestion des erreurs 404 (Page non trouvée).
    
    Args:
        error (Exception): L'erreur générée.
    
    Returns:
        str: Réponse JSON avec un message d'erreur et un code de statut 404.
    """
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(401)
def unauthorized(error: Exception) -> Tuple[jsonify, int]:
    """Gestion des erreurs 401 (Non autorisé).
    
    Args:
        error (Exception): L'erreur générée.
    
    Returns:
        Tuple[jsonify, int]: Réponse JSON avec un message d'erreur et un code de statut 401.
    """
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def forbidden(error: Exception) -> Tuple[jsonify, int]:
    """Gestion des erreurs 403 (Interdit).
    
    Args:
        error (Exception): L'erreur générée.
    
    Returns:
        Tuple[jsonify, int]: Réponse JSON avec un message d'erreur et un code de statut 403.
    """
    return jsonify({"error": "Forbidden"}), 403


@app.before_request
def handle_request():
    """
    Traite la requête en vérifiant l'authentification et l'autorisation.
    """
    # Si auth est None, ne rien faire et continuer
    if auth is None:
        return

    # Liste des chemins d'URL exclus de l'authentification
    excluded_paths = ['/api/v1/status/',
                      '/api/v1/unauthorized/',
                      '/api/v1/forbidden/',
                      '/api/v1/auth_session/login/']
    
    # Si le chemin de la requête ne nécessite pas d'authentification, ne rien faire
    if not auth.require_auth(request.path, excluded_paths):
        return
    
    # Récupère l'en-tête d'autorisation et le cookie de session
    auth_header = auth.authorization_header(request)
    session_cookie = auth.session_cookie(request)
    
    # Si ni l'en-tête d'autorisation ni le cookie de session ne sont présents, lancer une erreur 401
    if auth_header is None and session_cookie is None:
        abort(401)
    
    # Si l'utilisateur courant est None, lancer une erreur 403
    user = auth.current_user(request)
    if user is None:
        abort(403)
    
    # Assigner l'utilisateur courant à l'objet de requête
    request.current_user = user


if __name__ == "__main__":
    # Lecture de l'hôte et du port depuis les variables d'environnement
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    # Démarrage de l'application Flask avec le mode debug activé
    app.run(host=host, port=port, debug=True)
