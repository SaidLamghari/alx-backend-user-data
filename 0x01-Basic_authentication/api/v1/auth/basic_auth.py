#!/usr/bin/env python3
"""
Module d'authentification
de base pour l'API.
"""
import re
from typing import TypeVar
import base64
from models.user import User
import binascii
from .auth import Auth
from typing import Tuple


# Définition d'un type générique pour l'utilisateur
UserType = TypeVar('User')


class BasicAuth(Auth):
    """
    Classe d'authentification
    de base.
    """
    def extract_base64_authorization_header(self,
                                            authorization_header: str) -> str:
        """Extrait la partie Base64 de l'en-tête Authorization
        pour une authentification de base.

        Args:
            authorization_header (str): L'en-tête
            Authorization contenant le token d'authentification.

        Returns:
            str: Le token Base64 extrait de
            l'en-tête, ou None si l'en-tête n'est pas valide.
        """

        if not isinstance(authorization_header, str):
            return None

        if isinstance(authorization_header, str):
            # Motif pour extraire la partie Base64 de l'en-tête Authorization
            motif = r'Basic (?P<token>.+)'
            match_terrain = re.fullmatch(motif, authorization_header.strip())
            if match_terrain is not None:
                return match_terrain.group('token')

    def decode_base64_authorization_header(self,
                                           base64_authorization_header: str
                                           ) -> str:
        """Décode un en-tête d'autorisation encodé en base64.

        Args:
            base64_authorization_header (str):
                L'en-tête d'autorisation encodé en base64.

        Returns:
            str: Le contenu décodé de l'en-tête,
            ou None si le décodage échoue.
        """
        if base64_authorization_header is None:
            return None

        if isinstance(base64_authorization_header, str):
            try:
                # Décode la chaîne Base64
                rslt = base64.b64decode(
                    base64_authorization_header,
                    validate=True,
                )
                return rslt.decode('utf-8')
            except (binascii.Error, UnicodeDecodeError):
                # Gestion des erreurs de décodage
                return None

    def extract_user_credentials(self,
                                 decoded_base64_authorization_header: str,
                                 ) -> Tuple[str, str]:
        """Extrait les informations d'identification de
        l'utilisateur à partir de l'en-tête d'autorisation décodé
        qui utilise le flux d'authentification de base.

        Args:
            decoded_base64_authorization_header (str):
            L'en-tête d'autorisation décodé en texte clair.

        Returns:
            Tuple[str, str]: Un tuple contenant l'email et le mot
            de passe de l'utilisateur, ou (None, None) si l'extraction échoue.
        """
        if decoded_base64_authorization_header is None:
            return None, None

        if isinstance(decoded_base64_authorization_header, str):
            # Motif pour extraire l'email et le mot de passe
            motif = r'(?P<user>[^:]+):(?P<password>.+)'
            match_terrain = re.fullmatch(
                motif,
                decoded_base64_authorization_header.strip(),
            )
            if match_terrain is not None:
                user = match_terrain.group('user')
                password = match_terrain.group('password')
                return user, password

    def user_object_from_credentials(self,
                                     user_email: str,
                                     user_pwd: str) -> UserType:
        """Récupère un utilisateur basé sur les informations
        d'identification de l'utilisateur.

        Args:
            user_email (str): L'email de l'utilisateur.
            user_pwd (str): Le mot de passe de l'utilisateur.

        Returns:
            UserType: L'objet utilisateur correspondant aux informations
            d'identification, ou None si l'utilisateur
            n'existe pas ou si le mot de passe est invalide.
        """
        if user_email is None or not isinstance(user_email, str):
            return None

        if user_pwd is None or not isinstance(user_pwd, str):
            return None

        if isinstance(user_email, str) and isinstance(user_pwd, str):
            try:
                # Recherche de l'utilisateur par email
                users = User.search({'email': user_email})
            except Exception:
                # Gestion des exceptions lors de la recherche d'utilisateur
                return None
            if len(users) <= 0:
                return None
            # Vérification du mot de passe de l'utilisateur
            if users[0].is_valid_password(user_pwd):
                return users[0]

    def current_user(self, request=None) -> UserType:
        """Récupère l'utilisateur à partir d'une requête.

        Args:
            request (Flask Request, optional): La requête Flask
            contenant l'en-tête d'autorisation. Par défaut, None.

        Returns:
            UserType: L'utilisateur actuellement
            authentifié, ou None si l'authentification échoue.
        """
        # Extraction de l'en-tête d'autorisation
        entete = self.authorization_header(request)
        # Extraction du token Base64 de l'en-tête
        b64_entete = self.extract_base64_authorization_header(entete)
        # Décodage du token Base64
        tknofauth = self.decode_base64_authorization_header(b64_entete)
        # Extraction des informations d'identification de l'utilisateur
        email, password = self.extract_user_credentials(tknofauth)
        # Récupération de l'objet utilisateur basé
        # sur les informations d'identification
        return self.user_object_from_credentials(email, password)
