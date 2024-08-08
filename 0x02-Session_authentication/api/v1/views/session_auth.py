#!/usr/bin/env python3
"""
Module des vues d'authentification par session.
Auteuur SAID LAMGHARI
"""
import os
from typing import Tuple
from api.v1.app import auth

from flask import abort
from flask import jsonify, request
from models.user import User
from api.v1.views import app_views


@app_views.route('/auth_session/login',
                 methods=['POST'], strict_slashes=False)
def for_login() -> Tuple[str, int]:
    """POST /api/v1/auth_session/login
    Cette route permet à un utilisateur de se connecter
    en fournissant un email et un mot de passe.

    Retourne :
      - Une réponse JSON représentant l'objet utilisateur
      si l'authentification est réussie.
      - 400 si l'email ou le mot de passe est manquant.
      - 404 si aucun utilisateur n'est trouvé avec cet email.
      - 401 si le mot de passe est incorrect.
    """
    no_rslt = {"error": "no user found for this email"}

    # Récupère l'email et le mot de passe de la requête
    email = request.form.get('email')
    if email is None or len(email.strip()) == 0:
        # Retourne une erreur si l'email est manquant ou vide
        return jsonify({"error": "email missing"}), 400

    password = request.form.get('password')
    if password is None or len(password.strip()) == 0:
        # Retourne une erreur si le mot de passe est manquant ou vide
        return jsonify({"error": "password missing"}), 400

    try:
        # Recherche les utilisateurs par email
        users = User.search({'email': email})
    except Exception:
        # Retourne une erreur 404 en cas d'exception durant la recherche
        return jsonify(no_rslt), 404

    if len(users) <= 0:
        # Retourne une erreur 404 si aucun utilisateur n'est trouvé
        return jsonify(no_rslt), 404

    if users[0].is_valid_password(password):
        # Si le mot de passe est valide,
        # crée une session et retourne l'utilisateur
        session_id = auth.create_session(getattr(users[0], 'id'))
        rslt = jsonify(users[0].to_json())
        # Définit le cookie de session dans la réponse
        rslt.set_cookie(os.getenv("SESSION_NAME"), session_id)
        return rslt

    # Retourne une erreur 401 si le mot de passe est incorrect
    return jsonify({"error": "wrong password"}), 401


@app_views.route('/auth_session/logout',
                 methods=['DELETE'], strict_slashes=False)
def for_logout() -> Tuple[str, int]:
    """DELETE /api/v1/auth_session/logout
    Cette route permet à un utilisateur de
    se déconnecter en détruisant la session.

    Retourne :
      - Un objet JSON vide si la déconnexion est réussie.
      - 404 si la session ne peut pas être détruite.
    """
    # Tente de détruire la session de l'utilisateur
    for_delet = auth.destroy_session(request)
    if not for_delet:
        # Retourne une erreur 404 si la
        # session ne peut pas être détruite
        abort(404)

    # Retourne un objet JSON vide si la déconnexion est réussie
    return jsonify({})
