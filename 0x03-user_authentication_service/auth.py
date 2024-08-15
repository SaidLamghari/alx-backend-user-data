#!/usr/bin/env python3
"""
Ce module implémente les routines liées
à l'authentification des utilisateurs,
y compris l'enregistrement, la gestion des sessions,
et la réinitialisation des mots de passe.
Auteur SAID LAMGHARI
"""
from user import User
import bcrypt
from uuid import uuid4
from typing import Union
from sqlalchemy.orm.exc import NoResultFound
from db import DB


def _generate_uuid() -> str:
    """
    9. Generate UUIDs
    _generate_uuid function in the auth module
    """
    return str(uuid4())


def _hash_password(pssword: str) -> bytes:
    """
    Hache un mot de
    passe en utilisant bcrypt.

    Arguments:
        - password (str): Le mot de
        passe en texte clair.

    Retourne:
        - bytes: Le mot de passe
        haché sous forme de bytes.
    """
    return bcrypt.hashpw(pssword.encode("utf-8"),
                         bcrypt.gensalt())


class Auth:
    """
    La classe Auth gère les opérations
    d'authentification des utilisateurs,
    y compris l'enregistrement, la validation
    des identifiants de connexion,
    la gestion des sessions et la
    réinitialisation des mots de passe.
    """

    def __init__(self):
        """
        Initialise une nouvelle instance
        de la classe Auth.

        Cette méthode initialise une connexion
        à la base de données en instanciant
        la classe DB.
        """
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """
        Enregistre un nouvel utilisateur
        dans la base de données.

        Cette méthode vérifie d'abord si l'email
        existe déjà. Si non, elle crée un nouvel
        utilisateur avec l'email et le mot de passe haché.

        Arguments:
            - email (str): L'email de
            l'utilisateur à enregistrer.
            - password (str): Le mot de passe
            en texte clair de l'utilisateur.

        Retourne:
            - User: L'objet User nouvellement créé.

        Lève:
            - ValueError: Si l'utilisateur
            avec cet email existe déjà.
        """
        try:
            # Vérifie si l'utilisateur existe déjà
            self._db.find_user_by(email=email)
        except NoResultFound:
            # Ajoute l'utilisateur si non trouvé
            return self._db.add_user(email, _hash_password(password))
        # Lève une exception si l'utilisateur existe déjà
        raise ValueError(f"User {email} already exists")

    def valid_login(self, email: str, password: str) -> bool:
        """
        Vérifie si les détails de connexion
        d'un utilisateur sont valides.

        Cette méthode hache le mot de passe
        fourni et le compare avec le mot de passe
        haché stocké dans la base de données.

        Arguments:
            - email (str): L'email de l'utilisateur.
            - password (str): Le mot de passe en texte clair.

        Retourne:
            - bool: True si les identifiants
            sont valides, False sinon.
        """
        try:
            user = self._db.find_user_by(email=email)
            if user is not None:
                return bcrypt.checkpw(password.encode("utf-8"),
                                      user.hashed_password)
        except NoResultFound:
            return False  # Retourne False si aucun utilisateur n'est trouvé
        return False  # Retourne False par défaut si la vérification échoue

    def create_session(self, email: str) -> Union[str, None]:
        """
        Crée une nouvelle session pour un utilisateur.

        Cette méthode génère un identifiant
        de session unique (UUID) et l'associe
        à l'utilisateur correspondant à l'email fourni.

        Arguments:
            - email (str): L'email de l'utilisateur.

        Retourne:
            - str: L'ID de session nouvellement créé.
            - None: Si l'utilisateur n'existe pas.
        """
        try:
            varuser = self._db.find_user_by(email=email)
        except NoResultFound:
            return None  # Retourne None si l'utilisateur n'est pas trouvé
        sessid = _generate_uuid  # Génère un UUID pour la session
        # Met à jour l'utilisateur avec le nouvel ID de session
        self._db.update_user(varuser.id, session_id=sessid)
        return sessid

    def get_user_from_session_id(self,
                                 session_id: str) -> Union[User, None]:
        """
        Récupère un utilisateur basé sur un ID de session donné.

        Arguments:
            - session_id (str): L'ID de session de l'utilisateur.

        Retourne:
            - User: L'objet User correspondant à l'ID de session.
            - None: Si aucun utilisateur n'est
            trouvé ou si l'ID de session est invalide.
        """
        if session_id is None:
            # Retourne None si l'ID de session est None
            return None
        try:
            # Recherche l'utilisateur par ID de session
            return self._db.find_user_by(session_id=session_id)
        except NoResultFound:
            # Retourne None si aucun utilisateur n'est trouvé
            return None

    def destroy_session(self, user_id: int) -> None:
        """
        Détruit une session associée à un utilisateur donné.

        Cette méthode supprime l'ID de session de l'utilisateur,
        ce qui équivaut à déconnecter l'utilisateur.

        Arguments:
            - user_id (int): L'ID de l'utilisateur
            dont la session doit être détruite.
        """
        if user_id is None:
            return None  # Ne rien faire si l'ID de l'utilisateur est None
        # Met à jour l'utilisateur en supprimant l'ID de session
        self._db.update_user(user_id, session_id=None)

    def get_reset_password_token(self, email: str) -> str:
        """
        Génère un jeton de réinitialisation
        de mot de passe pour un utilisateur.

        Cette méthode génère un UUID pour la
        réinitialisation du mot de passe et
        l'associe à l'utilisateur
        correspondant à l'email fourni.

        Arguments:
            - email (str): L'email de l'utilisateur.

        Retourne:
            - str: Le jeton de réinitialisation
            de mot de passe.

        Lève:
            - ValueError: Si aucun utilisateur n'est trouvé pour cet email.
        """
        try:
            varuser = self._db.find_user_by(email=email)
        except NoResultFound:
            # Lève une exception si aucun utilisateur n'est trouvé
            raise ValueError("User not found")
        # Génère un UUID pour la réinitialisation
        resetoken = _generate_uuid
        # Met à jour l'utilisateur avec le nouveau jeton
        self._db.update_user(varuser.id, reset_token=resetoken)
        return resetoken

    def update_password(self, reset_token: str,
                        password: str) -> None:
        """
        Met à jour le mot de passe d'un utilisateur
        donné un jeton de réinitialisation valide.

        Cette méthode recherche l'utilisateur par
        son jeton de réinitialisation, hache
        le nouveau mot de passe,
        et met à jour la base de données.

        Arguments:
            - reset_token (str): Le jeton de
            réinitialisation de l'utilisateur.
            - password (str): Le nouveau mot
            de passe en texte clair.

        Lève:
            - ValueError: Si aucun utilisateur
            n'est trouvé pour ce jeton.
        """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
        except NoResultFound:
            # Lève une exception si le jeton est invalide
            raise ValueError("Invalid reset token")
        # Hache le nouveau mot de passe
        nwpsswordforhash = _hash_password(password)
        self._db.update_user(
            user.id,
            hashed_password=nwpsswordforhash,
            # Supprime le jeton de réinitialisation après utilisation
            reset_token=None,
        )
