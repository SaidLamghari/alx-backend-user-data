#!/usr/bin/env python3
"""
Module d'authentification pour l'API.
Auteur SAID LAMGHARI
"""
import os
from flask import request
import re
from typing import List
from typing import TypeVar


class Auth:
    """
    Classe d'authentification.
    Cette classe fournit des méthodes de base
    pour gérer l'authentification des requêtes API.
    """
    def require_auth(self, path: str,
                     excluded_paths: List[str]) -> bool:
        """Vérifie si un chemin nécessite une authentification.

        Arguments :
          - path : Chemin de l'URL de la requête.
          - excluded_paths : Liste des chemins
          d'URL qui sont exclus de l'authentification.

        Retourne :
          - True si le chemin nécessite une authentification.
          - False si le chemin est dans
          les chemins exclus de l'authentification.
        """
        if not path:
            return True

        # Assure que les paramètres ne sont pas None
        if path and excluded_paths:
            # Parcourt chaque chemin d'exclusion
            # en supprimant les espaces superflus
            for exclusion_path in (ep.strip() for ep in excluded_paths):
                # Détermine le motif de correspondance
                # en fonction du type de chemin d'exclusion
                if exclusion_path.endswith('*'):
                    # Exclusion avec étoile (*), correspond
                    # à tout chemin commençant par exclusion_path
                    pattern = f'{exclusion_path[:-1]}.*'
                elif exclusion_path.endswith('/'):
                    # Exclusion avec un slash (/), correspond
                    # à tout chemin sous exclusion_path
                    pattern = f'{exclusion_path[:-1]}/.*'
                else:
                    # Exclusion simple, correspond à
                    # tout chemin sous exclusion_path
                    pattern = f'{exclusion_path}/.*'

                # Vérifie si le chemin de la requête
                # correspond au motif d'exclusion
                if re.match(pattern, path):
                    return False

        # Retourne True si aucune correspondance
        # avec les chemins exclus n'est trouvée
        return True

    def authorization_header(self,
                             request=None) -> str:
        """Récupère le champ d'en-tête
        d'autorisation de la requête.

        Arguments :
          - request : Requête HTTP en cours.

        Retourne :
          - La valeur de l'en-tête
          d'autorisation si elle est présente.
          - None si l'en-tête d'autorisation est absent.
        """
        # Vérifie que la requête est fournie
        if request is not None:
            # Retourne la valeur de l'en-tête
            # 'Authorization' de la requête
            return request.headers.get('Authorization', None)
        return None

    def current_user(self, request=None) -> TypeVar('User'):
        """Récupère l'utilisateur courant de la requête.

        Arguments :
          - request : Requête HTTP en cours.

        Retourne :
          - L'utilisateur courant
          (défini dans les sous-classes).
          - None par défaut dans la classe de base.
        """
        return None

    def session_cookie(self,
                       request=None) -> str:
        """Récupère la valeur du cookie nommé SESSION_NAME.

        Arguments :
          - request : Requête HTTP en cours.

        Retourne :
          - La valeur du cookie nommé SESSION_NAME
          si la requête est fournie.
          - None si la requête est absente
          ou le cookie n'est pas trouvé.
        """
        # Vérifie que la requête est fournie
        if request is not None:
            # Récupère le nom du cookie depuis
            # les variables d'environnement
            ckie_name = os.getenv('SESSION_NAME')
            # Retourne la valeur du cookie nommé SESSION_NAME
            return request.cookies.get(ckie_name)
        return None
