#!/usr/bin/env python3
"""
Module de vues pour
l'authentification par session.
Auteur SAID LAMGHARI
"""
import os
from typing import Tuple
from flask import abort
from flask import jsonify
from flask import request
from api.v1.views import app_views
from models.user import User


@app_views.route('/auth_session/login',
                 methods=['POST'], strict_slashes=False)
def login() -> Tuple[str, int]:
    """Route POST pour /api/v1/auth_session/login
    Authentifie un utilisateur et crée une
    session si les informations sont valides.
    
    Retourne:
      - La représentation JSON d'un objet User en cas de succès.
      - Une réponse d'erreur avec un code
      d'état approprié en cas d'échec.
    """
    # Message de réponse pour
    # l'absence d'utilisateur avec cet email
    no_rslt = {"error": "no user found for this email"}
    
    # Récupération de l'email et du mot de
    # passe depuis le formulaire de la requête
    email = request.form.get('email')
    var_lenemail = len(email.strip())
    if email is None or var_lenemail == 0:
        # Retourne une erreur 400 si l'email est manquant ou vide
        return jsonify({"error": "email missing"}), 400
    
    password = request.form.get('password')
    var_lenpass = len(password.strip())
    if password is None or var_lenpass == 0:
        # Retourne une erreur 400 si
        # le mot de passe est manquant ou vide
        return jsonify({"error": "password missing"}), 400
    
    try:
        # Recherche d'un utilisateur avec l'email fourni
        users = User.search({'email': email})
    except Exception:
        # Retourne une erreur 404 en
        # cas d'exception durant la recherche
        return jsonify(no_rslt), 404
    
    # Vérifie si aucun utilisateur n'a été trouvé
    var_len = len(users)
    if var_len <= 0:
        return jsonify(no_rslt), 404
    
    # Vérifie si le mot de passe fourni est valide
    if users[0].is_valid_password(password):
        # Importation de l'objet
        # d'authentification depuis l'application
        from api.v1.app import auth
        
        # Création d'une session et récupération de l'ID de session
        sssionid = auth.create_session(getattr(users[0], 'id'))
        
        # Création de la réponse JSON avec les informations de l'utilisateur
        rslt = jsonify(users[0].to_json())
        
        # Définition du cookie de session avec l'ID de session
        rslt.set_cookie(os.getenv("SESSION_NAME"), sssionid)
        
        return rslt
    
    # Retourne une erreur 401 si le mot de passe est incorrect
    return jsonify({"error": "wrong password"}), 401

@app_views.route(
    '/auth_session/logout', methods=['DELETE'], strict_slashes=False)
def logout() -> Tuple[str, int]:
    """Route DELETE pour /api/v1/auth_session/logout
    Déconnecte l'utilisateur en détruisant la session active.
    
    Retourne:
      - Un objet JSON vide en cas de succès.
      - Une erreur 404 si la destruction de la session échoue.
    """
    # Importation de l'objet d'authentification depuis l'application
    from api.v1.app import auth
    
    # Tentative de destruction de la session active
    idestroyed = auth.destroy_session(request)
    
    # Retourne une erreur 404 si
    # la session n'a pas pu être détruite
    if not idestroyed:
        abort(404)
    
    # Retourne un objet JSON vide en cas de succès
    return jsonify({})
