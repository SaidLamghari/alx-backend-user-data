#!/usr/bin/env python3
"""Module des vues des utilisateurs.
"""
from flask import abort
from flask import jsonify
from flask import request
from models.user import User
from api.v1.views import app_views


@app_views.route('/users',
                 methods=['GET'], strict_slashes=False)
def for_view_all_users() -> str:
    """GET /api/v1/users
    Retourne :
      - Liste de tous les objets User représentés en JSON.
    """
    # Récupère tous les utilisateurs de la base
    # de données et les convertit en format JSON
    jsall_users = [user.to_json() for user in User.all()]
    # Retourne la liste des utilisateurs en format JSON
    return jsonify(jsall_users)


@app_views.route('/users/<user_id>',
                 methods=['GET'], strict_slashes=False)
def for_view_one_user(user_id: str = None) -> str:
    """GET /api/v1/users/:id
    Paramètre de chemin :
      - ID de l'utilisateur.
    Retourne :
      - L'objet User représenté en JSON.
      - 404 si l'ID de l'utilisateur n'existe pas.
    """
    # Vérifie si l'ID de l'utilisateur est fourni
    if user_id is None:
        abort(404)
    # Cas spécial pour l'ID 'me',
    # retourne les informations de l'utilisateur courant
    if user_id == 'me':
        if request.current_user is None:
            abort(404)
        else:
            return jsonify(request.current_user.to_json())
    # Récupère l'utilisateur par ID
    user = User.get(user_id)
    # Retourne une erreur 404 si l'utilisateur n'existe pas
    if user is None:
        abort(404)
    # Retourne l'objet utilisateur en format JSON
    return jsonify(user.to_json())


@app_views.route('/users/<user_id>',
                 methods=['DELETE'], strict_slashes=False)
def for_delete_user(user_id: str = None) -> str:
    """DELETE /api/v1/users/:id
    Paramètre de chemin :
      - ID de l'utilisateur.
    Retourne :
      - JSON vide si l'utilisateur a été correctement supprimé.
      - 404 si l'ID de l'utilisateur n'existe pas.
    """
    # Vérifie si l'ID de l'utilisateur est fourni
    if user_id is None:
        abort(404)
    # Récupère l'utilisateur par ID
    user = User.get(user_id)
    # Retourne une erreur 404 si l'utilisateur n'existe pas
    if user is None:
        abort(404)
    # Supprime l'utilisateur
    user.remove()
    # Retourne un JSON vide avec un code de statut 200 (OK)
    return jsonify({}), 200


@app_views.route('/users',
                 methods=['POST'], strict_slashes=False)
def for_create_user() -> str:
    """POST /api/v1/users/
    Corps de la requête JSON :
      - email.
      - password.
      - last_name (optionnel).
      - first_name (optionnel).
    Retourne :
      - L'objet User représenté en JSON.
      - 400 si la création du nouvel utilisateur échoue.
    """
    dmndjson = None
    mssgderreur = None
    try:
        # Essaye de récupérer le corps de la requête en format JSON
        dmndjson = request.get_json()
    except Exception as e:
        dmndjson = None
    # Vérifie si le corps de la requête est présent
    if dmndjson is None:
        mssgderreur = "Wrong format"
    # Vérifie que les champs email et password sont présents
    if mssgderreur is None and dmndjson.get("email", "") == "":
        mssgderreur = "email missing"
    if mssgderreur is None and dmndjson.get("password", "") == "":
        mssgderreur = "password missing"
    # Essaye de créer un nouvel utilisateur avec les données fournies
    if mssgderreur is None:
        try:
            user = User()
            user.email = dmndjson.get("email")
            user.password = dmndjson.get("password")
            user.first_name = dmndjson.get("first_name")
            user.last_name = dmndjson.get("last_name")
            user.save()
            # Retourne l'objet utilisateur créé en format
            # JSON avec un code de statut 201 (Créé)
            return jsonify(user.to_json()), 201
        except Exception as e:
            mssgderreur = "Can't create User : {}".format(e)
    # Retourne un message d'erreur en format JSON
    # avec un code de statut 400 (Mauvaise requête)
    return jsonify({'error': mssgderreur}), 400


@app_views.route('/users/<user_id>',
                 methods=['PUT'], strict_slashes=False)
def for_update_user(user_id: str = None) -> str:
    """PUT /api/v1/users/:id
    Paramètre de chemin :
      - ID de l'utilisateur.
    Corps de la requête JSON :
      - last_name (optionnel).
      - first_name (optionnel).
    Retourne :
      - L'objet User représenté en JSON.
      - 404 si l'ID de l'utilisateur n'existe pas.
      - 400 si la mise à jour de l'utilisateur échoue.
    """
    # Vérifie si l'ID de l'utilisateur est fourni
    if user_id is None:
        abort(404)
    # Récupère l'utilisateur par ID
    user = User.get(user_id)
    # Retourne une erreur 404 si l'utilisateur n'existe pas
    if user is None:
        abort(404)
    dmndjson = None
    try:
        # Essaye de récupérer le corps de la requête en format JSON
        dmndjson = request.get_json()
    except Exception as e:
        dmndjson = None
    # Vérifie si le corps de la requête est présent
    if dmndjson is None:
        return jsonify({'error': "Format incorrect"}), 400
    # Met à jour les champs de l'utilisateur
    # s'ils sont fournis dans le corps de la requête
    if dmndjson.get('first_name') is not None:
        user.first_name = dmndjson.get('first_name')
    if dmndjson.get('last_name') is not None:
        user.last_name = dmndjson.get('last_name')
    # Sauvegarde les modifications
    user.save()
    # Retourne l'objet utilisateur mis à jour en
    # format JSON avec un code de statut 200 (OK)
    return jsonify(user.to_json()), 200
