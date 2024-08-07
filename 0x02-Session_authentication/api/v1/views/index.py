#!/usr/bin/env python3
"""Module des vues Index.
"""
from flask import jsonify, abort
from api.v1.views import app_views


# Route pour vérifier le statut de l'API
@app_views.route('/status', methods=['GET'], strict_slashes=False)
def status() -> str:
    """GET /api/v1/status
    Retourne :
      - Le statut de l'API sous la forme d'un
      JSON avec la clé "status" et la valeur "OK".
    """
    return jsonify({"status": "OK"})


# Route pour obtenir des statistiques
# sur les objets dans la base de données
@app_views.route('/stats/', strict_slashes=False)
def stats() -> str:
    """GET /api/v1/stats
    Retourne :
      - Le nombre d'objets pour chaque type
      d'objet (ici, le nombre d'utilisateurs).
    """
    # Importation du modèle User pour
    # accéder à la méthode de comptage
    from models.user import User
    stats = {}
    # Compte le nombre d'objets de type User et
    # stocke le résultat dans le dictionnaire stats
    stats['users'] = User.count()
    return jsonify(stats)


# Route pour générer une erreur 401 - Non autorisé
@app_views.route('/unauthorized/', strict_slashes=False)
def unauthorizedroute() -> None:
    """GET /api/v1/unauthorized
    Retourne :
      - Une erreur 401 - Non autorisé.
    """
    # Interrompt le traitement de la
    # requête et retourne une réponse 401
    abort(401)


# Route pour générer une erreur 403 - Interdit
@app_views.route('/forbidden/', strict_slashes=False)
def forbiddenroute() -> None:
    """GET /api/v1/forbidden
    Retourne :
      - Une erreur 403 - Interdit.
    """
    # Interrompt le traitement de la requête
    # et retourne une réponse 403
    abort(403)
