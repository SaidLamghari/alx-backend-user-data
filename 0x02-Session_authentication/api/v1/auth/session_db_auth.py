#!/usr/bin/env python3
"""Module d'authentification
par session avec expiration
et support de stockage pour l'API.
"""
from flask import request
from typing import Optional

from models.user_session import UserSession
from .session_exp_auth import SessionExpAuth
from datetime import datetime, timedelta


class SessionDBAuth(SessionExpAuth):
    """Classe d'authentification par session avec
    expiration et support de stockage.
    """

    def create_session(self, user_id: Optional[str] = None) -> Optional[str]:
        """Crée et stocke un identifiant de session pour l'utilisateur.

        Args:
            user_id (str, optionnel): L'identifiant de
            l'utilisateur pour lequel créer la session.

        Retourne:
            str: L'identifiant de session créé si
            la session a été stockée avec succès.
            None: Si la session ne peut pas être créée ou stockée.
        """
        # Crée un identifiant de session en
        # utilisant la méthode de la classe parente
        session_id = super().create_session(user_id)
        if isinstance(session_id, str):
            # Crée une nouvelle instance de UserSession avec
            # l'identifiant de l'utilisateur et de la session
            user_session = UserSession(user_id=user_id, session_id=session_id)
            try:
                # Tente de sauvegarder la session dans la base de données
                user_session.save()
            except Exception as e:
                # Gère les exceptions lors de la sauvegarde
                # (journalisation ou autres actions peuvent être ajoutées)
                print(f"Erreur lors de la sauvegarde de la session : {e}")
                return None
            return session_id
        return None

    def user_id_for_session_id(self,
                               session_id: Optional[str] = None
                               ) -> Optional[str]:
        """Récupère l'identifiant de l'utilisateur
        associé à un identifiant de session donné.

        Args:
            session_id (str, optionnel): L'identifiant de
            session pour lequel récupérer l'identifiant de l'utilisateur.

        Retourne:
            str: L'identifiant de l'utilisateur
            si la session est valide et non expirée.
            None: Si la session est invalide ou
            expirée, ou si une erreur se produit.
        """
        if not session_id:
            return None

        try:
            # Recherche les sessions dans la base de
            # données avec l'identifiant de session fourni
            sessions = UserSession.search({'session_id': session_id})
        except Exception as e:
            # Gère les exceptions lors de la recherche
            # (journalisation ou autres actions peuvent être ajoutées)
            print(f"Erreur lors de la recherche de la session : {e}")
            return None

        if not sessions:
            return None

        # Calcule le délai d'expiration de la session
        # Date et heure actuelles
        current_dtetime = datetime.now()
        # Durée de la session en tant que timedelta
        session_duration = timedelta(seconds=self.session_duration)
        # Date et heure d'expiration
        expiration_dtetime = sessions[0].created_at + session_duration

        if expiration_dtetime < current_dtetime:
            # Retourne None si la session est expirée
            return None

        return sessions[0].user_id

    def destroy_session(self, request: Optional[request] = None) -> bool:
        """Déconnecte une session authentifiée.

        Args:
            request (flask.Request, optionnel):
            La requête HTTP contenant le cookie de session.

        Retourne:
            bool: True si la session a été supprimée
            avec succès, False sinon.
        """
        # Récupère l'identifiant de session à partir du cookie de la requête
        session_id = self.session_cookie(request)
        if not session_id:
            return False

        try:
            # Recherche les sessions dans la base de données
            # avec l'identifiant de session fourni
            sessions = UserSession.search({'session_id': session_id})
        except Exception as e:
            # Gère les exceptions lors de la recherche
            # (journalisation ou autres actions peuvent être ajoutées)
            print(f"Erreur lors de la recherche de la session : {e}")
            return False

        if not sessions:
            return False

        try:
            # Supprime la session trouvée de la base de données
            sessions[0].remove()
        except Exception as e:
            # Gère les exceptions lors de la suppression
            # (journalisation ou autres actions peuvent être ajoutées)
            print(f"Erreur lors de la suppression de la session : {e}")
            return False

        return True
