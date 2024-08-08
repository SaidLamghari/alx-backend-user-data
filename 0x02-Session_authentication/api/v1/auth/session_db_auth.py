#!/usr/bin/env python3
"""Module d'authentification de session avec expiration
et prise en charge du stockage pour l'API.
Auteur SAID LAMGHARI
"""
from flask import request

from models.user_session import UserSession

from datetime import datetime, timedelta


from .session_exp_auth import SessionExpAuth


class SessionDBAuth(SessionExpAuth):
    """Classe d'authentification de session
    avec expiration et prise en charge du stockage.
    """

    def create_session(self,
                       user_id=None) -> str:
        """Crée et stocke un identifiant de session pour l'utilisateur.

        Args:
            user_id (str): L'identifiant de l'utilisateur
            pour lequel créer la session.

        Returns:
            str: L'identifiant de session créé.
        """
        # Appelle la méthode de la classe parente pour créer une session
        sessionforid = super().create_session(user_id)
        if type(sessionforid) == str:
            # Prépare les arguments pour créer une instance de UserSession
            kwargs = {
                'user_id': user_id,
                'session_id': sessionforid,
            }
            # Crée et enregistre une nouvelle session
            # utilisateur dans la base de données
            user_session = UserSession(**kwargs)
            user_session.save()
            return sessionforid

    def user_id_for_session_id(self,
                               session_id=None):
        """Récupère l'identifiant de l'utilisateur associé
        à un identifiant de session donné.

        Args:
            session_id (str): L'identifiant de session pour
            lequel obtenir l'identifiant utilisateur.

        Returns:
            str: L'identifiant de l'utilisateur associé à la session,
            ou None si la session est invalide ou expirée.
        """
        try:
            # Recherche les sessions avec l'identifiant fourni
            v_sessons = UserSession.search({'session_id': session_id})
        except Exception:
            # En cas d'erreur lors de la recherche, retourne None
            return None

        # Vérifie si aucune session n'a été trouvée
        var_len = len(v_sessons)

        if var_len <= 0:
            return None

        # Récupère l'heure actuelle
        # Calcule le temps d'expiration de la session
        session_drtion = timedelta(seconds=self.session_duration)

        expration_dtetime = v_sessons[0].created_at + session_drtion

        # Vérifie si la session est expirée
        if expration_dtetime < datetime.now():
            return None

        # Retourne l'identifiant de
        # l'utilisateur associé à la session
        return v_sessons[0].user_id

    def destroy_session(self,
                        request=None) -> bool:
        """Détruit une session authentifiée.

        Args:
            request (Request): La requête
            contenant le cookie de session.

        Returns:
            bool: True si la session a été
            détruite avec succès, sinon False.
        """
        # Récupère l'identifiant de la session
        # depuis le cookie de la requête
        sessionforid = self.session_cookie(request)
        try:
            # Recherche les sessions avec l'identifiant fourni
            v_sessions = UserSession.search({'session_id': sessionforid})
        except Exception:
            # En cas d'erreur lors de la recherche, retourne False
            return False

        # Vérifie si aucune session n'a été trouvée
        var_ln = len(v_sessions)

        if var_ln <= 0:
            return False

        # Supprime la première session trouvée
        v_sessions[0].remove()
        return True
