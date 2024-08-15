#!/usr/bin/env python3
"""
Ce module définit les routes principales
de l'application Flask pour
la gestion de l'authentification des utilisateurs.
"""

from flask import Flask, request, jsonify, abort, redirect
from auth import Auth

app = Flask(__name__)
AUTH = Auth()


@app.route("/", methods=["GET"])
def index() -> str:
    """
    Route pour la page d'accueil.

    Cette route répond à une requête GET
    à la racine ("/") de l'application web.
    Elle renvoie un objet JSON contenant un message de bienvenue.

    Notes:
        - Le paramètre `strict_slashes=False` dans le décorateur
        de route permet d'accéder à la page d'accueil
        avec ou sans barre oblique finale.
        - La fonction utilise `jsonify`
        pour formater la réponse en JSON.
    """
    return jsonify({"message": "Bienvenue"})


@app.route('/users', methods=['POST'])
def for_register_user() -> str:
    """
    Enregistre un nouvel utilisateur avec l'email
    et le mot de passe fournis.

    Reçoit les données utilisateur dans le corps
    de la requête POST sous la forme de
    'email' et 'password'. Si l'email est déjà
    enregistré, retourne un message d'erreur
    avec un code de statut HTTP 400.
    Sinon, crée un nouvel utilisateur et retourne
    les détails de l'utilisateur avec un message de succès.

    :return: Une réponse JSON contenant
            l'email et un message indiquant si
            l'utilisateur a été créé ou
            si l'email est déjà enregistré.
    """
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        user = AUTH.register_user(email, password)
        return jsonify({"email": user.email, "message": "user created"})
        # return jsonify({"email": user.email, "message": "utilisateur créé"})
    except ValueError:
        return jsonify({"message": "email already registered"}), 400
        # return jsonify({"message": "email déjà enregistré"}), 400


@app.route('/sessions', methods=['POST'])
def for_login() -> str:
    """
    Connecte un utilisateur avec
    un email et un mot de passe fournis.

    Reçoit les données de connexion dans
    le corps de la requête POST sous la forme
    de 'email' et 'password'. Si les informations
    sont valides, crée une session pour
    l'utilisateur et retourne une réponse
    JSON avec l'email et un message de succès,
    ainsi qu'un cookie de session.
    Si les informations sont incorrectes, retourne une
    erreur HTTP 401.

    :return: Une réponse JSON contenant l'email
            et un message de succès si la connexion
            est réussie, sinon une erreur HTTP 401.
    """
    email = request.form.get('email')
    password = request.form.get('password')
    if AUTH.valid_login(email, password):
        session_id = AUTH.create_session(email)
        # response = jsonify({"email": email, "message": "connexion réussie"})
        rspnse = jsonify({"email": email, "message": "logged in"})
        rspnse.set_cookie("session_id", session_id)
        return rspnse
    else:
        abort(401)


@app.route('/sessions', methods=['DELETE'])
def for_logout() -> str:
    """
    Déconnecte un utilisateur en détruisant la session active.

    Reçoit le cookie de session de la requête
    et utilise l'ID de session pour trouver
    l'utilisateur. Si l'utilisateur est trouvé,
    la session est détruite et l'utilisateur
    est redirigé vers la page d'accueil.
    Sinon, retourne une erreur HTTP 403.

    :return: Une redirection vers la page d'accueil
            si la déconnexion est réussie,
            sinon une erreur HTTP 403.
    """
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if user:
        AUTH.destroy_session(user.id)
        return redirect('/')
    else:
        abort(403)


@app.route('/profile', methods=['GET'])
def for_profile() -> str:
    """
    Récupère le profil de l'utilisateur connecté.

    Utilise le cookie de session pour trouver
    l'utilisateur. Si la session est valide,
    retourne l'email de l'utilisateur sous forme
    de réponse JSON. Sinon, retourne une
    erreur HTTP 403.

    :return: Une réponse JSON contenant l'email
            de l'utilisateur si la session est
            valide, sinon une erreur HTTP 403.
    """
    session_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(session_id)
    if user:
        return jsonify({"email": user.email})
    else:
        abort(403)


@app.route('/reset_password', methods=['POST'])
def get_reset_password_token() -> str:
    """
    Génère un token de réinitialisation de
    mot de passe pour un utilisateur.

    Reçoit l'email de l'utilisateur dans le
    corps de la requête POST. Si l'email est
    valide, un token de réinitialisation est
    généré et retourné sous forme de réponse
    JSON. Si l'email n'est pas valide,
    retourne une erreur HTTP 403.

    :return: Une réponse JSON contenant
            l'email et le token de réinitialisation si
            l'email est valide, sinon une erreur HTTP 403.
    """
    email = request.form.get('email')
    try:
        reset_token = AUTH.get_reset_password_token(email)
        return jsonify({"email": email, "reset_token": reset_token})
    except ValueError:
        abort(403)


@app.route('/reset_password', methods=['PUT'])
def update_password() -> str:
    """
    Met à jour le mot de passe d'un utilisateur
    en utilisant un token de réinitialisation.

    Reçoit l'email de l'utilisateur, le token de
    réinitialisation, et le nouveau mot de
    passe dans le corps de la requête PUT.
    Si le token est valide, le mot de passe est
    mis à jour et une réponse JSON de succès
    est retournée. Sinon, retourne une erreur
    HTTP 403.

    :return: Une réponse JSON contenant l'email
            et un message de succès si le mot de
            passe est mis à jour avec succès,
            sinon une erreur HTTP 403.
    """
    email = request.form.get('email')
    reset_token = request.form.get('reset_token')
    new_password = request.form.get('new_password')
    try:
        AUTH.update_password(reset_token, new_password)
        # return jsonify({"email": email, "message":
        # "Mot de passe mis à jour"})
        return jsonify({"email": email, "message": "Password updated"})
    except ValueError:
        abort(403)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
