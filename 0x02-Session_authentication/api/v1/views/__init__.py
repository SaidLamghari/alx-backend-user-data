#!/usr/bin/env python3
""" DocDocDocDocDocDoc
"""
from flask import Blueprint

# Création du Blueprint pour les vues de l'API
# 'app_views' est le nom du blueprint,
# '__name__' est utilisé pour le chemin
# 'url_prefix="/api/v1"' définit le préfixe
# d'URL pour toutes les routes dans ce blueprint
app_views = Blueprint("app_views", __name__, url_prefix="/api/v1")

# Importation des routes définies dans les modules de vues
# Ces importations sont nécessaires
# pour enregistrer les routes auprès du blueprint
from api.v1.views.index import *
from api.v1.views.users import *

# Chargement des données
# d'utilisateur à partir d'un fichier
# Cela peut inclure des utilisateurs
# préexistants ou des configurations
User.load_from_file()

# Importation des routes liées à
# l'authentification par session
# Assure que les routes d'authentification
# sont disponibles pour l'API
from api.v1.views.session_auth import *
