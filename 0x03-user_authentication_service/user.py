#!/usr/bin/env python3
"""
Ce module définit la classe User,
représentant un utilisateur
dans la base de données.
Il utilise SQLAlchemy pour mapper
la classe aux tables de la base de données.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

# Création de la base déclarative pour SQLAlchemy
Base = declarative_base()


class User(Base):
    """
    La classe User représente un
    utilisateur dans la base de données.
    Elle est mappée à la table 'users'
    et contient les colonnes suivantes :

    - id (Integer): Identifiant unique de l'utilisateur, clé primaire.
    - email (String(250)): Adresse email
    de l'utilisateur, doit être unique et non nulle.
    - hashed_password (String(250)): Mot de passe
            haché de l'utilisateur, non nul.
    - session_id (String(250)): ID de session
            de l'utilisateur, peut être nul.
    - reset_token (String(250)): Token de réinitialisation
            du mot de passe, peut être nul.

    La classe hérite de `Base`, ce qui permet
    à SQLAlchemy de l'utiliser pour créer
    la table correspondante dans la base
    de données et de gérer les opérations CRUD.
    """
    # Nom de la table dans la base de données
    __tablename__ = 'users'

    # Colonne pour l'identifiant unique de l'utilisateur
    id = Column(Integer, primary_key=True)

    # Colonne pour l'adresse email de l'utilisateur, doit être unique
    email = Column(String(250), nullable=False, unique=True)

    # Colonne pour le mot de passe haché de l'utilisateur
    hashed_password = Column(String(250), nullable=False)

    # Colonne pour l'ID de session de l'utilisateur (peut être nul)
    session_id = Column(String(250), nullable=True)

    # Colonne pour le token de réinitialisation du mot de passe (peut être nul)
    reset_token = Column(String(250), nullable=True)
