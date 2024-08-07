#!/usr/bin/env python3
"""
Module d'authentification
par session pour l'API.
auteuur SAID LAMGHARI
"""
from uuid import uuid4

from models.user import User

from flask import request

from .auth import Auth


class SessionAuth(Auth):
    """
    Classe d'authentification par session.
    Cette classe gère la création, la récupération,
    et la destruction des sessions utilisateurs.
    """
    # Dictionnaire pour stocker les identifiants
    # des utilisateurs par identifiant de session
    user_id_by_session_id = {}

    def create_session(self,
                       user_id: str = None) -> str:
        """
        Crée un identifiant de session pour l'utilisateur.

        Arguments :
          - user_id : Identifiant de l'utilisateur
          pour lequel créer la session.

        Retourne :
          - Identifiant de session nouvellement
          créé sous forme de chaîne de caractères.
        """
        # Vérifie que user_id est bien une chaîne de caractères
        if type(user_id) is str:
            # Génère un nouvel identifiant de session unique
            session_id = str(uuid4())
            # Associe l'identifiant de session
            # à l'identifiant de l'utilisateur
            self.user_id_by_session_id[session_id] = user_id
            # Retourne l'identifiant de session
            return session_id

    def user_id_for_session_id(self,
                               session_id: str = None) -> str:
        """Récupère l'identifiant de l'utilisateur
        associé à un identifiant de session donné.

        Arguments :
          - session_id : Identifiant de session pour
          lequel récupérer l'identifiant de l'utilisateur.

        Retourne :
          - Identifiant de l'utilisateur
          associé à l'identifiant de session.
        """
        # Vérifie que session_id est bien une chaîne de caractères
        if type(session_id) is str:
            # Retourne l'identifiant de l'utilisateur
            # correspondant à l'identifiant de session
            return self.user_id_by_session_id.get(session_id)

    def current_user(self,
                     request=None) -> User:
        """
        Récupère l'utilisateur associé à la requête en cours.

        Arguments :
          - request : Requête HTTP en cours.

        Retourne :
          - Objet User correspondant à
          l'utilisateur associé à la session.
        """
        # Récupère l'identifiant de session
        # depuis les cookies de la requête
        session_id = self.session_cookie(request)
        # Récupère l'identifiant de l'utilisateur
        # associé à l'identifiant de session
        user_id = self.user_id_for_session_id(session_id)
        # Récupère l'objet User correspondant
        # à l'identifiant de l'utilisateur
        return User.get(user_id)

    def destroy_session(self,
                        request=None):
        """Détruit une session authentifiée.

        Arguments :
          - request : Requête HTTP en cours.

        Retourne :
          - True si la session a été détruite avec succès.
          - False si la session n'existe pas
          ou si une erreur est survenue.
        """
        # Récupère l'identifiant de session
        # depuis les cookies de la requête
        session_id = self.session_cookie(request)
        # Récupère l'identifiant de l'utilisateur
        # associé à l'identifiant de session
        user_id = self.user_id_for_session_id(session_id)
        # Vérifie si la requête et
        # l'identifiant de session sont valides
        if (request is None or session_id is None) or user_id is None:
            return False
        # Supprime l'identifiant de
        # session du dictionnaire s'il existe
        if session_id in self.user_id_by_session_id:
            del self.user_id_by_session_id[session_id]
        # Retourne True pour indiquer
        # que la session a été détruite
        return True
