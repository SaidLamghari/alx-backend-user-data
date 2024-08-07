#!/usr/bin/env python3
"""
Module de routage pour l'API.
Auteur SAID LAMGHARI
"""

from flask_cors import CORS
import os
from os import getenv
from flask import Flask
from flask import jsonify
from flask import abort
from flask import request
from api.v1.auth.session_auth import SessionAuth
from api.v1.views import app_views
from api.v1.auth.auth import Auth
from api.v1.auth.session_exp_auth import SessionExpAuth
from api.v1.auth.basic_auth import BasicAuth
from api.v1.auth.session_db_auth import SessionDBAuth


# Création de l'application Flask
app = Flask(__name__)

# Enregistrement du blueprint des vues de l'API
app.register_blueprint(app_views)

# Configuration de CORS (Cross-Origin Resource Sharing)
# Permet les requêtes de n'importe
# quelle origine sur les chemins de l'API
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

# Initialisation de la variable d'authentification
auth = None

# Détermination du type d'authentification à utiliser
# à partir des variables d'environnement
auth_type = getenv('AUTH_TYPE', 'auth')

# Création de l'objet d'authentification
# en fonction du type spécifié
if auth_type == 'auth':
    auth = Auth()
elif auth_type == 'session_auth':
    auth = SessionAuth()
elif auth_type == 'basic_auth':
    auth = BasicAuth()
elif auth_type == 'session_db_auth':
    auth = SessionDBAuth()
elif auth_type == 'session_exp_auth':
    auth = SessionExpAuth()


# Gestionnaire d'erreur
# 404 - Ressource non trouvée
@app.errorhandler(404)
def not_found(error) -> str:
    """
    Gestionnaire pour les erreurs 404
    - Ressource non trouvée.
    """
    return jsonify({"error": "Not found"}), 404


# Gestionnaire d'erreur 401 - Non autorisé
@app.errorhandler(401)
def unauthrzd_errorhandler(error) -> str:
    """
    Gestionnaire pour les
    erreurs 401 - Non autorisé.
    """
    return jsonify({"error": "Unauthorized"}), 401


# Gestionnaire d'erreur 403 - Interdit
@app.errorhandler(403)
def forbddn_errorhandler(error) -> str:
    """Gestionnaire pour les
    erreurs 403 - Interdit.
    """
    return jsonify({"error": "Forbidden"}), 403


# Fonction appelée avant le traitement de chaque requête
@app.before_request
def authenticate_usr_beforerequest():
    """Authentifie un utilisateur avant
    le traitement d'une requête.
    """
    if auth:
        # Liste des chemins d'URL exclus
        # de l'authentification
        excluded_paths = [
            "/api/v1/status/",  # Route pour vérifier le statut de l'API
            # Route pour tester les erreurs d'autorisation
            "/api/v1/unauthorized/",
            # Route pour tester les erreurs d'interdiction
            "/api/v1/forbidden/",
            # Route pour la connexion des sessions
            "/api/v1/auth_session/login/"
        ]

        # Vérifie si le chemin de la requête

        if not auth.require_auth(request.path, excluded_paths):
            return

        # Vérifie si le chemin de la requête
        # nécessite une authentification
        if auth.require_auth(request.path, excluded_paths):
            # Récupère l'utilisateur actuel basé sur la requête
            user = auth.current_user(request)
            # Si l'en-tête d'autorisation et le cookie de session sont absents
            if auth.authorization_header(request) is None and \
                    auth.session_cookie(request) is None:
                # Retourne une erreur 401 (Non autorisé)
                abort(401)
            # Si l'utilisateur est non identifié,
            # retourne une erreur 403 (Interdit)
            if user is None:
                abort(403)
            # Assigne l'utilisateur authentifié à la requête
            request.current_user = user


# Exécution de l'application Flask
if __name__ == "__main__":
    # Récupération de l'hôte et du port
    # depuis les variables d'environnement,
    # avec des valeurs par défaut si les
    # variables ne sont pas définies
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    # Lancement de l'application sur l'hôte et le port spécifiés
    app.run(host=host, port=port)
