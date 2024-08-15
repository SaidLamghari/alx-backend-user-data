#!/usr/bin/env python3
"""
Ce module gère l'interaction avec la
base de données en
utilisant SQLAlchemy.
"""

from user import User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from typing import Dict, Any


class DB:
    """
    La classe DB gère les opérations CRUD
    sur les utilisateurs
    dans la base de données.
    """

    def __init__(self) -> None:
        """Initialise la connexion à la base
        de données SQLite et configure la session."""
        self._engine = create_engine("sqlite:///user_auth.db", echo=False)
        User.metadata.create_all(self._engine)
        self._session = sessionmaker(bind=self._engine)()

    def add_user(self, email: str, hashed_password: str) -> User:
        """
        Ajoute un nouvel utilisateur
        dans la base de données.
        Retourne l'utilisateur ajouté.
        """
        varuser = User(email=email, hashed_password=hashed_password)
        self._session.add(varuser)
        self._session.commit()
        return varuser

    def find_user_by(self, **kwargs: Dict[str, Any]) -> User:
        """
        Trouve un utilisateur en
        fonction des critères spécifiés.
        Retourne l'utilisateur correspondant
        ou lève une exception NoResultFound.
        """
        return self._session.query(User).filter_by(**kwargs).one()

    def update_user(self, user_id: int, **kwargs: Dict[str, Any]) -> None:
        """
        Met à jour les champs
        spécifiés de l'utilisateur.
        """
        varuser = self.find_user_by(id=user_id)
        for ky, vlue in kwargs.items():
            setattr(varuser, ky, vlue)
        self._session.commit()
