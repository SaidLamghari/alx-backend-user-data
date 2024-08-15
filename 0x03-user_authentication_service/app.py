#!/usr/bin/env python3
"""
Ce module implémente une application Flask simple avec
des fonctionnalités d'authentification utilisateur.
Il permet de gérer l'inscription, la connexion,
la déconnexion, la récupération de profil,
et la réinitialisation du mot de passe pour les utilisateurs.
Auteur SAID LAMGHARI
"""

from flask import Flask, jsonify, request
from flask import redirect
from flask import redirect
from auth import Auth

# Initialisation de l'application Flask
app = Flask(__name__)

# Création d'une instance de la classe
# Auth pour gérer les opérations d'authentification
AUTH = Auth()


@app.route("/", methods=["GET"],
           strict_slashes=False)
def index_home() -> str:
    """
    Route d'accueil (GET /)
    Retourne un message de bienvenue.

    Retour:
        - JSON contenant le message de bienvenue.
    """
    return jsonify({"message": "Bienvenue"})


@app.route("/users", methods=["POST"],
           strict_slashes=False)
def for_register_user() -> str:
    """
    Route pour l'inscription des utilisateurs (POST /users)

    Cette route permet à un utilisateur de créer un
    compte en fournissant un email et un mot de passe.
    Si l'email est déjà enregistré, une erreur est retournée.

    Retour:
        - JSON confirmant la création du compte ou un
        message d'erreur si l'email est déjà enregistré.
    """
    email = request.form.get("email")
    pssword = request.form.get("password")

    try:
        # Tentative d'inscription de l'utilisateur
        # avec l'email et le mot de passe fournis
        AUTH.register_user(email, pssword)
        return jsonify({"email": email, "message": "user created"})
    except ValueError:
        # Si l'email est déjà enregistré, retourner
        # une erreur 400 avec un message d'avertissement
        return jsonify({"message": "email already registered"}), 400


@app.route("/sessions", methods=["POST"],
           strict_slashes=False)
def for_login() -> str:
    """
    Route pour la connexion des utilisateurs (POST /sessions)

    Cette route permet à un utilisateur de se connecter
    en fournissant un email et un mot de passe valides.
    Si les informations de connexion sont correctes, une
    session est créée et un cookie de session est défini.

    Retour:
        - JSON confirmant la connexion ou une erreur
        401 si les informations sont incorrectes.
    """
    email = request.form.get("email")
    pssword = request.form.get("password")

    # Vérification des informations de connexion
    if not AUTH.valid_login(email, pssword):
        # Retourne une erreur 401 si l'email
        # ou le mot de passe est incorrect
        abort(401)

    # Création d'une session pour l'utilisateur
    # et définition d'un cookie de session
    session_id = AUTH.create_session(email)
    rspnse = jsonify({"email": email, "message": "logged in"})
    rspnse.set_cookie("session_id", session_id)

    return rspnse


@app.route("/sessions",
           methods=["DELETE"], strict_slashes=False)
def for_logout() -> str:
    """
    Route pour la déconnexion des utilisateurs (DELETE /sessions)

    Cette route permet à un utilisateur de
    se déconnecter en détruisant sa session actuelle.
    Si la session est invalide, une erreur 403 est retournée.

    Retour:
        - Redirection vers la page d'accueil après déconnexion
        ou une erreur 403 si la session est invalide.
    """
    session_id = request.cookies.get("session_id")
    varusr = AUTH.get_user_from_session_id(session_id)

    if varusr is None:
        # Retourne une erreur 403 si la session est invalide
        abort(403)

    # Destruction de la session de l'utilisateur
    AUTH.destroy_session(varusr.id)

    return redirect("/")


@app.route("/profile",
           methods=["GET"], strict_slashes=False)
def for_profile() -> str:
    """
    Route pour récupérer le profil de
    l'utilisateur connecté (GET /profile)

    Cette route retourne l'email de
    l'utilisateur associé à la session actuelle.
    Si la session est invalide,
    une erreur 403 est retournée.

    Retour:
        - JSON contenant l'email de l'utilisateur
        ou une erreur 403 si la session est invalide.
    """
    session_id = request.cookies.get("session_id")
    varuser = AUTH.get_user_from_session_id(session_id)

    if varuser is None:
        # Retourne une erreur 403 si la session est invalide
        abort(403)

    return jsonify({"email": varuser.email})


@app.route("/reset_password",
           methods=["POST"], strict_slashes=False)
def for_get_reset_password_token() -> str:
    """
    Route pour obtenir un jeton de réinitialisation
    de mot de passe (POST /reset_password)

    Cette route génère un jeton de réinitialisation
    pour l'utilisateur associé à l'email fourni.
    Si l'email n'est pas enregistré, une erreur 403 est retournée.

    Retour:
        - JSON contenant l'email de l'utilisateur
        et le jeton de réinitialisation,
          ou une erreur 403 si l'email
          n'est pas enregistré.
    """
    email = request.form.get("email")
    resetoken = None

    try:
        # Tentative de génération d'un jeton
        # de réinitialisation pour l'utilisateur
        resetoken = AUTH.get_reset_password_token(email)
    except ValueError:
        resetoken = None

    if resetoken is None:
        # Retourne une erreur 403 si l'email n'est pas enregistré
        abort(403)

    return jsonify({"email": email, "reset_token": resetoken})


@app.route("/reset_password",
           methods=["PUT"], strict_slashes=False)
def for_update_password() -> str:
    """
    Route pour mettre à jour le mot de passe
    d'un utilisateur (PUT /reset_password)

    Cette route permet de mettre à jour le mot de passe
    de l'utilisateur en utilisant le jeton de réinitialisation.
    Si le jeton est invalide, une erreur 403 est retournée.

    Retour:
        - JSON confirmant la mise à jour du mot de
        passe ou une erreur 403 si le jeton est invalide.
    """
    email = request.form.get("email")
    resetoken = request.form.get("reset_token")
    nwpassword = request.form.get("new_password")
    passwordchanged = False

    try:
        # Tentative de mise à jour du mot de passe de l'utilisateur
        AUTH.update_password(resetoken, nwpassword)
        passwordchanged = True
    except ValueError:
        passwordchanged = False

    if not passwordchanged:
        # Retourne une erreur 403 si le jeton est invalide
        abort(403)

    return jsonify({"email": email, "message": "Password updated"})


if __name__ == "__main__":
    # Démarrage de l'application Flask sur le port 5000
    app.run(host="0.0.0.0", port="5000")
