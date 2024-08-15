#!/usr/bin/env python3
"""
Ce module implémente une classe DB pour gérer
les opérations de base de données
liées aux utilisateurs à l'aide de SQLAlchemy.
Il permet d'ajouter, de rechercher,
et de mettre à jour des utilisateurs
dans une base de données SQLite.
"""
from user import User
from sqlalchemy import create_engine, tuple_
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from user import Base


class DB:
    """
    La classe DB gère les interactions avec
    la base de données pour les opérations
    liées aux utilisateurs. Elle utilise SQLAlchemy
    pour interagir avec une base de
    données SQLite.
    """

    def __init__(self) -> None:
        """
        Initialise une nouvelle instance de la classe DB.

        Cette méthode configure la connexion
        à la base de données SQLite,
        réinitialise les tables existantes
        (supprime et recrée) et initialise
        l'objet de session à None.
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        # Supprime toutes les tables existantes
        Base.metadata.drop_all(self._engine)
        # Crée toutes les tables définies dans le modèle
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """
        Propriété pour accéder à l'objet de
        session de manière mémorisée.

        Si la session n'a pas encore été initialisée,
        cette méthode crée une nouvelle
        session liée au moteur de base de données.

        Retourne:
            - Un objet SQLAlchemy Session pour
            interagir avec la base de données.
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """
        Ajoute un nouvel utilisateur dans la base de données.

        Cette méthode crée un nouvel utilisateur
        avec l'email et le mot de passe hashé
        fournis, l'ajoute à la session, et le
        sauvegarde dans la base de données.

        Arguments:
            - email (str): L'email de l'utilisateur.
            - hashed_password (str): Le mot de
            passe hashé de l'utilisateur.

        Retourne:
            - L'objet User nouvellement créé
            si l'ajout est réussi, sinon None.
        """
        try:
            nwuser = User(email=email, hashed_password=hashed_password)
            # Ajoute le nouvel utilisateur à la session
            self._session.add(nwuser)
            # Valide la transaction et sauvegarde les changements
            self._session.commit()
        except Exception:
            # Annule la transaction en cas d'erreur
            self._session.rollback()
            nwuser = None
        return nwuser

    def find_user_by(self, **kwargs) -> User:
        """
        Trouve un utilisateur en fonction
        d'un ensemble de filtres.

        Cette méthode prend des paires clé-valeur
        correspondant aux attributs de la classe
        User et les utilise pour rechercher
        un utilisateur dans la base de données.

        Arguments:
            - kwargs: Paires clé-valeur correspondant
            aux attributs du modèle User.

        Retourne:
            - L'objet User correspondant aux filtres.

        Lève:
            - InvalidRequestError: Si une clé fournie
            ne correspond pas à un attribut du modèle User.
            - NoResultFound: Si aucun
            utilisateur ne correspond aux filtres.
        """
        chps, vls = [], []
        for ky, value in kwargs.items():
            if hasattr(User, ky):
                chps.append(getattr(User, ky))
                vls.append(value)
            else:
                # Lève une exception si la clé n'est pas un attribut valide
                raise InvalidRequestError()
        rslt = self._session.query(User).filter(
            tuple_(*chps).in_([tuple(vls)])
        ).first()
        # Recherche le premier utilisateur correspondant aux filtres
        if rslt is None:
            # Lève une exception si aucun utilisateur n'est trouvé
            raise NoResultFound()
        return rslt

    def update_user(self, user_id: int, **kwargs) -> None:
        """
        Met à jour les informations
        d'un utilisateur en fonction de son ID.

        Cette méthode trouve l'utilisateur
        correspondant à l'ID fourni et met à jour
        ses attributs en fonction
        des paires clé-valeur fournies.

        Arguments:
            - user_id (int): L'ID de l'utilisateur à mettre à jour.
            - kwargs: Paires clé-valeur des attributs à mettre à jour.

        Retourne:
            - None

        Lève:
            - ValueError: Si une clé fournie ne
            correspond pas à un attribut du modèle User.
        """
        # Recherche l'utilisateur par son ID
        varuser = self.find_user_by(id=user_id)
        if varuser is None:
            # Si l'utilisateur n'existe pas, ne rien faire
            return
        updatsource = {}
        for ky, value in kwargs.items():
            if hasattr(User, ky):
                # Prépare les champs à mettre à jour
                updatsource[getattr(User, ky)] = value
            else:
                # Lève une exception si la clé n'est pas un attribut valide
                raise ValueError()
        self._session.query(User).filter(User.id == user_id).update(
            updatsource,
            synchronize_session=False,
        )  # Met à jour les champs spécifiés
        # Valide la transaction et sauvegarde les changements
        self._session.commit()
