#!/usr/bin/env python3
"""
Module pour la gestion du hachage
et de la validation des mots de passe.
Auteur : SAID LAMGHARI
"""

import bcrypt


def hash_password(password: str) -> bytes:
    """
    Hache un mot de passe en utilisant bcrypt.

    Arguments:
        password (str): Le mot de passe en clair à hacher.

    Retourne:
        bytes: Le mot de passe haché sous forme de bytes.

    Détails:
        - La fonction `bcrypt.hashpw` génère
        un hachage sécurisé du mot de passe.
        - `bcrypt.gensalt()` génère un sel (salt)
        aléatoire pour renforcer la sécurité du hachage.
        - Le mot de passe en clair est d'abord
        encodé en bytes avant le hachage.
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def is_valid(hashed_password: bytes, password: str) -> bool:
    """
    Vérifie si un mot de passe donné correspond au mot de passe haché.

    Arguments:
        hashed_password (bytes): Le mot de passe haché à comparer.
        password (str): Le mot de passe en clair à vérifier.

    Retourne:
        bool: True si le mot de passe correspond, False sinon.

    Détails:
        - La fonction `bcrypt.checkpw` compare le mot
        de passe en clair avec le mot de passe haché.
        - Le mot de passe en clair est encodé en bytes avant la comparaison.
        - `bcrypt.checkpw` utilise le même sel que celui
        utilisé pour le hachage pour vérifier la correspondance.
    """
    return bcrypt.checkpw(password.encode(), hashed_password)
