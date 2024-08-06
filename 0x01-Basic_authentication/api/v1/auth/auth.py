#!/usr/bin/env python3
"""Module d'authentification pour l'API.
"""

from flask import request
from typing import TypeVar
from typing import List
import re


# Définition d'un type générique pour l'utilisateur
TypeofUser = TypeVar('User')


class Auth:
    """Authentification.
    """
    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        """Vérifie si un chemin nécessite une authentification.

        Args:
            path (str): Le chemin de la requête à vérifier.
            excluded_paths (List[str]): Liste des
            chemins exclus de l'authentification.

        Returns:
            bool: Retourne True si le chemin nécessite
            une authentification, False sinon.
        """
        # Si aucune correspondance n'est trouvée dans
        # les chemins exclus, l'authentification est requise
        if path is None:
            return True
        if excluded_paths is None or len(excluded_paths) == 0:
            return True
        if path is not None and excluded_paths is not None:
            # Itération sur chaque chemin exclu en
            # supprimant les espaces superflus
            for exclusion_path in map(lambda x: x.strip(), excluded_paths):
                motif = ''
                # Création du motif de correspondance basé
                # sur le format du chemin exclu
                if exclusion_path[-1] == '*':
                    # Si le chemin se termine par '*', cela indique
                    # un motif de correspondance partielle
                    motif = '{}.*'.format(exclusion_path[0:-1])
                elif exclusion_path[-1] == '/':
                    # Si le chemin se termine par '/', cela indique
                    # une correspondance pour tous les sous-chemins
                    motif = '{}/*'.format(exclusion_path[0:-1])
                else:
                    # Sinon, correspondance exacte du chemin
                    motif = '{}/*'.format(exclusion_path)
                # Vérifie si le chemin de la requête correspond au motif
                if re.match(motif, path):
                    return False

    def authorization_header(self, request=None) -> str:
        """Obtient le champ d'en-tête d'autorisation de la requête.

        Args:
            request (Flask Request, optional): La requête
            Flask dont extraire l'en-tête. Par défaut, None.

        Returns:
            str: La valeur de l'en-tête
            'Authorization', ou None s'il n'existe pas.
        """
        if request is not None:
            return request.headers.get('Authorization', None)
        return None

    def current_user(self, request=None) -> TypeofUser:
        """Obtient l'utilisateur actuel à partir de la requête.

        Args:
            request (Flask Request, optional): La requête Flask dont
            extraire les informations de l'utilisateur. Par défaut, None.

        Returns:
            TypeofUser: L'utilisateur actuel, ou None
            si aucune authentification n'est effectuée.
        """
        return None
