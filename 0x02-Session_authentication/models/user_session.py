#!/usr/bin/env python3
"""Modèle de session utilisateur pour stocker
les sessions dans la base de données."""
from datetime import datetime
from typing import Optional, List, Dict
# Supposons que Base est votre classe de base pour l'ORM
from models.base import Base


class UserSession(Base):
    """Modèle de session utilisateur pour stocker les sessions."""

    def __init__(self, *args: list, **kwargs: dict):
        """Initialise une instance de UserSession.

        Args:
            *args (list): Arguments supplémentaires pour l'initialisation.
            **kwargs (dict): Arguments de mot-clé pour l'initialisation,
            incluant 'user_id', 'session_id', 'created_at', et 'updated_at'.

        Lève:
            ValueError: Si 'user_id' ou 'session_id'
            ne sont pas fournis dans kwargs.
        """
        # Vérifie que 'user_id' et 'session_id' sont présents dans kwargs
        if 'user_id' not in kwargs or 'session_id' not in kwargs:
            raise ValueError("user_id et session_id sont requis")

        # Initialise les attributs de la session utilisateur
        # Identifiant de l'utilisateur auquel la session appartient
        self.user_id = kwargs['user_id']
        # Identifiant unique de la session
        self.session_id = kwargs['session_id']
        # Date et heure de création de la session,
        # utilise la date actuelle si non fournie
        self.created_at = kwargs.get('created_at', datetime.now())
        # Date et heure de la dernière mise à jour de la session,
        # utilise la date actuelle si non fournie
        self.updated_at = kwargs.get('updated_at', datetime.now())

        # Appelle le constructeur de la classe
        # de base pour compléter l'initialisation
        super().__init__(*args, **kwargs)
