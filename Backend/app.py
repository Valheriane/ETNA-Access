import datetime
from faker import Faker
#from flask_restful import Api
from flask import Flask, request, jsonify
from urllib import request
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from models import db, Base
from populate_db import populate_all, populate_access_rights, populate_addresses, populate_all_hash, populate_companies, \
    populate_default_images, populate_fonctions, populate_images, populate_license_modes, populate_licenses, \
    populate_login_history, populate_oauth_providers, populate_offer_products, populate_offer_types, populate_offers, \
    populate_payment_methods, populate_permissions_sso, populate_product_configurations, populate_product_imgs, \
    populate_production_data, populate_products, populate_type_imgs, populate_user_logs, populate_user_oauth, \
    populate_user_sessions, populate_users, populate_defined_users
    


# Charger les variables d'environnement
load_dotenv(dotenv_path='app.env')

# Créer une instance de l'application
app = Flask(__name__)

# Configuration de la base de données
db_path = os.path.join(app.instance_path, 'my_database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fallback_secret_key')  # Récupérer la clé depuis .env
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(minutes=30)


# Créer le répertoire 'instance' s'il n'existe pas
os.makedirs(app.instance_path, exist_ok=True)

# Initialiser SQLAlchemy et Flask-Migrate
db.init_app(app)  # Correction ici
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
fake = Faker()



@app.cli.command("populate-prod-data")
def populate_prod_data():
    """Commande pour peupler la table type_imgs."""
    with app.app_context():  # Activer le contexte de l'application
        try:
            print("Initialisation de la base de donnees...")
            db.drop_all()
            print("Creation des tables...")
            db.create_all()  # Crée toutes les tables
            print("Début du peuplement de la bdd")
            populate_production_data()
            print("Peuplement terminé.")
        except Exception as e:
            print(f"Erreur lors du peuplement : {e}")

@app.cli.command("populate-all")
def populate_all_command():
    """Commande pour peupler toutes les tables de la base de données."""
    with app.app_context():  # Activer le contexte de l'application
        try:
            fake.unique.clear()
            print("Début du peuplement de la base de données...")
            populate_all(db)  # Appeler ta fonction de peuplement
            print("Peuplement terminé.")
        except Exception as e:
            print(f"Erreur lors du peuplement : {e}")


@app.cli.command("reset-db") #executer dans le terminale flask reset-db
def reset_db():
    """Réinitialiser et remplir la base de données avec des données de test."""
    with app.app_context():
        try:
            print("Reinitialisation de la base de donnees...")
            db.drop_all()  # Supprime toutes les tables
            print("Creation des tables...")
            db.create_all()  # Crée toutes les tables
            print("Insertion des donnees de test...")
            populate_all(db)  # Ajoute les données de test
            print("Base de données reinitialisée avec succes.")
        except Exception as e:
            print(f"Erreur lors de l'initialisation de la base de donnees : {e}")
            
            
@app.cli.command("reset-db-hash") #executer dans le terminale flask reset-db-hash
def reset_db():
    """Réinitialiser et remplir la base de données avec des données de test."""
    with app.app_context():
        try:
            print("Reinitialisation de la base de donnees...")
            db.drop_all()  # Supprime toutes les tables
            print("Creation des tables...")
            db.create_all()  # Crée toutes les tables
            print("Insertion des donnees de test...")
            populate_all_hash(db)  # Ajoute les données de test
            print("Base de données reinitialisee avec succes.")
            print("User Test : debut d intregration")
            populate_defined_users(db)
            print("User Test : fin d'intregration")
        except Exception as e:
            print(f"Erreur lors de l'initialisation de la base de donnees : {e}")


'''
with app.app_context():
    try:
        print("Reinitialisation de la base de donnees...")
        db.drop_all()  # Supprime toutes les tables
        print("Creation des tables...")
        db.create_all()  # Crée toutes les tables
        print("Insertion des donnees de test...")
        populate_all(db)  # Ajoute les données de test
        print("Base de données reinitialisée avec succes.")
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de donnees : {e}")

'''

def check_permissions(user_permission, target_user_id=None, user_id_from_token=None, company_id_from_token=None, target_company_id=None, target_user_permission=None):
    """
    Vérifie les permissions de l'utilisateur en fonction des règles définies.

    :param user_permission: Niveau de permission de l'utilisateur courant.
    :param target_user_id: Identifiant de l'utilisateur cible (facultatif).
    :param user_id_from_token: Identifiant de l'utilisateur courant.
    :param company_id_from_token: Identifiant de la compagnie de l'utilisateur courant.
    :param target_company_id: Identifiant de la compagnie cible.
    :param target_user_permission: Niveau de permission de l'utilisateur cible (facultatif).
    :return: True si l'utilisateur a le droit d'accès, False sinon.
    """
    print(" je suis dans check_permissions " )
    print(" user_id_from_token : ", user_id_from_token  , " et target_user_id : ", target_user_id  )
    print("target_user_permission ", target_user_permission, " et user_permission : ", user_permission)
    # Permissions 1-2 : Accès uniquement à ses propres informations
    if user_permission in [1, 2]:
        return target_user_id == user_id_from_token

    # Permissions 3-4 : Accès aux utilisateurs de la même entreprise
    if user_permission == 3:
        print(" je suis dans user_permission 3 " )
        if target_user_id == user_id_from_token:
            print(" je suis dans if target_user_id == user_id_from_token : target_user_id ", target_user_id )
            return True  # Peut toujours voir ses propres informations
        if target_company_id == company_id_from_token:
            print("DANS CHECK PERMISSION : target Company_id : ", target_company_id, " et company_id_from_token ", company_id_from_token)
            if target_user_permission and target_user_permission < 3:
                print(" je suis dans if target_company_id == company_id_from_token: : target_user_permission ", target_user_permission )
                return True  # Peut voir les membres de sa propre entreprise avec une permission inférieure à 7
            return False  # Ne peut pas voir les membres avec une permission >= 7
        if target_user_permission and target_user_permission >= 4:
            return False  # Ne peut pas voir les utilisateurs d'autres entreprises avec permission >= 7
        return False  # Pas d'accès aux utilisateurs d'autres entreprises
    
    # Permissions 3-4 : Accès aux utilisateurs de la même entreprise
    if user_permission == 4:
        return target_company_id == company_id_from_token

    # Permissions 5 : Accès limité selon des règles spécifiques
    if user_permission == 5:
        print(" je suis dans user_permission 5 :  " )
        if target_user_id == user_id_from_token:
            return True  # Peut toujours voir ses propres informations
        if target_company_id == company_id_from_token:
            return False  # Ne peut pas accéder aux membres de sa propre entreprise
        return True  # Accès par défaut (autres entreprises)

    # Permissions 6 : Accès spécifique pour les managers ETNA
    if user_permission == 6:
        print(" je suis dans user_permission 6 " )
        if target_user_id == user_id_from_token:
            print(" je suis dans if target_user_id == user_id_from_token : target_user_id ", target_user_id )
            return True  # Peut toujours voir ses propres informations
        if target_company_id == company_id_from_token:
            if target_user_permission and target_user_permission < 6:
                print(" je suis dans if target_company_id == company_id_from_token: : target_user_permission ", target_user_permission )
                return True  # Peut voir les membres de sa propre entreprise avec une permission inférieure à 7
            return False  # Ne peut pas voir les membres avec une permission >= 7
        if target_user_permission and target_user_permission >= 7:
            return False  # Ne peut pas voir les utilisateurs d'autres entreprises avec permission >= 7
        return True  # Pas d'accès aux utilisateurs d'autres entreprises

    # Permissions 7 ou plus : Accès à tout
    if user_permission >= 7:
        return True

    # Par défaut, accès refusé
    return False


