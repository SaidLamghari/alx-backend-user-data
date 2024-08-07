#!/usr/bin/env python3
"""Module d'authentification par session avec expiration pour l'API.
"""
import os
from flask import request
from .session_auth import SessionAuth
from datetime import datetime, timedelta


class SessionExpAuth(SessionAuth):
    """Classe d'authentification par session avec expiration.
    Cette classe gère les sessions utilisateurs avec une durée limitée.
    """

    def __init__(self) -> None:
        """Initialise une nouvelle instance de SessionExpAuth.
        """
        # Initialise la classe parente pour hériter des
        # attributs et méthodes de SessionAuth
        super().__init__()
        # Définit la durée de vie des sessions en récupérant
        # la valeur depuis les variables d'environnement
        self.session_duration = self._get_session_duration()

    def _get_session_duration(self) -> int:
        """Récupère la durée de vie des sessions à partir
        des variables d'environnement.

        Retourne:
            int: La durée de vie des sessions en secondes.
            Retourne 0 en cas de problème.
        """
        try:
            # Récupère la durée de session depuis la variable
            # d'environnement SESSION_DURATION
            return int(os.getenv('SESSION_DURATION', '0'))
        except ValueError:
            # Si la valeur de la variable d'environnement ne
            # peut pas être convertie en entier, retourne 0
            return 0

    def create_session(self, user_id=None) -> str:
        """Crée un identifiant de session pour l'utilisateur.

        Args:
            user_id (str): L'identifiant de
            l'utilisateur pour lequel créer la session.

        Retourne:
            str: L'identifiant de session créé. Retourne None en cas d'erreur.
        """
        # Utilise la méthode de la classe parente pour créer une session
        session_id = super().create_session(user_id)
        if not isinstance(session_id, str):
            # Si l'identifiant de session n'est pas
            # une chaîne de caractères, retourne None
            return None

        # Stocke les informations de la session, y compris
        # l'identifiant de l'utilisateur et la date de création
        self.user_id_by_session_id[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now(),
        }
        return session_id

    def user_id_for_session_id(self, session_id=None) -> str:
        """Récupère l'identifiant de l'utilisateur
        associé à un identifiant de session donné.

        Args:
            session_id (str): L'identifiant de session
            dont on souhaite obtenir l'identifiant de l'utilisateur.

        Retourne:
            str: L'identifiant de l'utilisateur si la
            session est valide et non expirée. Retourne None autrement.
        """
        # Récupère les informations de session
        # basées sur l'identifiant de session
        session_data = self.user_id_by_session_id.get(session_id)
        if session_data:
            if self.session_duration <= 0:
                # Si la durée de session est illimitée (0 ou moins),
                # retourne directement l'identifiant de l'utilisateur
                return session_data['user_id']

            # Récupère la date de création de la session
            created_at = session_data.get('created_at')
            if not created_at:
                # Si la date de création n'est pas disponible, retourne None
                return None

            # Calcule le temps d'expiration de la session
            extion_te = created_at + timedelta(seconds=self.session_duration)
            if datetime.now() < extion_te:
                # Si la session n'est pas encore
                # expirée, retourne l'identifiant de l'utilisateur
                return session_data['user_id']

        # Retourne None si la session est expirée ou invalide
        return None
