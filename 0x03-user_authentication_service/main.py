#!/usr/bin/env python3
"""
Ce fichier contient des tests d'intégration
de bout en bout pour vérifier
que toutes les fonctionnalités de
l'application fonctionnent correctement.
"""

import requests


def register_user(email: str, password: str) -> None:
    """
    Inscrit un utilisateur
    et vérifie que la
    réponse est correcte.
    """
    response = requests.post(
        'http://localhost:5000/users',
        data={'email': email, 'password': password}
    )
    assert response.status_code == 200, \
        f"Erreur lors de l'inscription: {response.status_code}"
    assert response.json() == {"email": email, "message": "utilisateur créé"}


def log_in_wrong_password(email: str, password: str) -> None:
    """
    Teste la connexion avec un mauvais
    mot de passe et vérifie que la
    connexion échoue.
    """
    response = requests.post(
        'http://localhost:5000/sessions',
        data={'email': email, 'password': password}
    )
    assert response.status_code == 401, \
        "La connexion avec un mauvais mot de passe devrait échouer"


def log_in(email: str, password: str) -> str:
    """
    Teste la connexion avec un bon mot
    de passe et retourne l'ID de session.
    """
    response = requests.post(
        'http://localhost:5000/sessions',
        data={'email': email, 'password': password}
    )
    assert response.status_code == 200, \
        "La connexion a échoué malgré de bons identifiants"
    return response.cookies.get('session_id')


def profile_unlogged() -> None:
    """
    Teste l'accès au profil
    sans être connecté.
    """
    response = requests.get('http://localhost:5000/profile')
    assert response.status_code == 403, \
        "L'accès au profil sans connexion devrait échouer"


def profile_logged(session_id: str) -> None:
    """
    Teste l'accès au profil en étant connecté.
    """
    response = requests.get(
        'http://localhost:5000/profile',
        cookies={'session_id': session_id}
    )
    assert response.status_code == 200, \
        "L'accès au profil a échoué malgré une connexion"


def log_out(session_id: str) -> None:
    """
    Teste la déconnexion et vérifie que
    la session est correctement détruite.
    """
    response = requests.delete(
        'http://localhost:5000/sessions',
        cookies={'session_id': session_id}
    )
    assert response.status_code == 200, "La déconnexion a échoué"


def reset_password_token(email: str) -> str:
    """
    Teste la génération d'un token de
    réinitialisation de mot de passe.
    Retourne le token généré.
    """
    response = requests.post(
        'http://localhost:5000/reset_password',
        data={'email': email}
    )
    assert response.status_code == 200, \
        "La génération du token de réinitialisation a échoué"
    return response.json().get('reset_token')


def update_password(email: str, reset_token: str, new_password: str) -> None:
    """
    Teste la mise à jour du mot de passe
    avec un token de réinitialisation
    valide.
    """
    response = requests.put(
        'http://localhost:5000/reset_password',
        data={
            'email': email,
            'reset_token': reset_token,
            'new_password': new_password
        }
    )
    assert response.status_code == 200, \
        "La mise à jour du mot de passe a échoué"


EMAIL = "guillaume@holberton.io"
PASSWD = "b4l0u"
NEW_PASSWD = "t4rt1fl3tt3"


if __name__ == "__main__":
    register_user(EMAIL, PASSWD)
    log_in_wrong_password(EMAIL, NEW_PASSWD)
    profile_unlogged()
    session_id = log_in(EMAIL, PASSWD)
    profile_logged(session_id)
    log_out(session_id)
    reset_token = reset_password_token(EMAIL)
    update_password(EMAIL, reset_token, NEW_PASSWD)
    log_in(EMAIL, NEW_PASSWD)
