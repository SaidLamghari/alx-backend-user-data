#!/usr/bin/env python3
"""
Ce module contient la classe Auth,
responsable de la gestion
de l'authentification des utilisateurs.
"""

import uuid
from db import DB
from user import User
from sqlalchemy.orm.exc import NoResultFound
import bcrypt
from typing import Optional


class Auth:
    """
    Auth gère les opérations d'authentification telles que
    l'inscription, la connexion,
    et la gestion des mots de passe.
    """

    def __init__(self) -> None:
        """Initialise l'instance Auth avec
        une instance de la base de données."""
        self._db = DB()

    def register_user(self, email: str,
                      password: str) -> User:
        """
        Enregistre un nouvel utilisateur
        avec un email et un mot de passe.
        Retourne l'utilisateur enregistré.
        """
        try:
            self._db.find_user_by(email=email)
            raise ValueError(f"Utilisateur {email} existe déjà")
        except NoResultFound:
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'),
                                      bcrypt.gensalt())
            user = self._db.add_user(email, hashed_pw)
            return user

    def valid_login(self, email: str, password: str) -> bool:
        """
        Vérifie si l'email et le mot de passe sont valides.
        Retourne True si la connexion est réussie, sinon False.
        """
        try:
            user = self._db.find_user_by(email=email)
            return bcrypt.checkpw(password.encode('utf-8'),
                                  user.hashed_password)
        except NoResultFound:
            return False

    def create_session(self, email: str) -> str:
        """
        Crée une session utilisateur et retourne l'ID de session.
        """
        user = self._db.find_user_by(email=email)
        session_id = str(uuid.uuid4())
        self._db.update_user(user.id, session_id=session_id)
        return session_id

    def get_user_from_session_id(self,
                                 session_id: Optional[str]) -> Optional[User]:
        """
        Retourne l'utilisateur correspondant à l'ID de session.
        Retourne None si la session n'est pas trouvée.
        """
        if session_id is None:
            return None
        try:
            user = self._db.find_user_by(session_id=session_id)
            return user
        except NoResultFound:
            return None

    def destroy_session(self, user_id: int) -> None:
        """
        Détruit la session de l'utilisateur spécifié.
        """
        self._db.update_user(user_id, session_id=None)

    def get_reset_password_token(self, email: str) -> str:
        """
        Génère un token de réinitialisation
        de mot de passe pour l'utilisateur.
        Retourne le token généré.
        """
        try:
            user = self._db.find_user_by(email=email)
            resettoken = str(uuid.uuid4())
            self._db.update_user(user.id,
                                 reset_token=resettoken)
            return resettoken
        except NoResultFound:
            raise ValueError("Invalid reset token")

    def update_password(self, reset_token: str,
                        password: str) -> None:
        """
        Met à jour le mot de passe de l'utilisateur
        en utilisant le token de réinitialisation.
        """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'),
                                      bcrypt.gensalt())
            self._db.update_user(user.id,
                                 hashed_password=hashed_pw, reset_token=None)
        except NoResultFound:
            raise ValueError("Invalid reset token")
