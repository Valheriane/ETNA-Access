from datetime import timedelta
import datetime
from random import  random, seed
from faker import Faker
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

from models import db, AccessRights, Address, Company, FonctionCompany, Images, License, LicenseMode, LogUserAction, LoginHistory, OAuthProvider, Offer, OfferProducts, OfferTypes, PaymentMethod, PermissionSSO, Product, ProductConfigurations, ProductImgs, TypeImgs, Users, UserOAuth, UserSession

fake = Faker()

# Initialisation des seeds
seed(42)  # Pour les fonctions aléatoires standards
fake.seed_instance(42)  # Pour Faker uniquement

def populate_defined_users(db):
    """Créer des utilisateurs définis et leur associer des permissions."""

    # Liste des utilisateurs à créer
    users_data = [
        {
            "first_name": "Emma",
            "last_name": "Sano",
            "email": "emma.sano@example.com",
            "phone": "0601020304",
            "phone_prefix_user": "+33",
            "password": "DrakenILoveYou!",
            "imgs_id": 1,  # ID d'image existant
            "fonction": "Particulier",
            "company_id": None,  # Pas d'entreprise, utilisateur indépendant
            "permission_id": 1 ,# Admin
            "statut":1,
            
        },
        {
            "first_name": "Licorne",
            "last_name": "UneBelle",
            "email": "licorne.unebelle@example.com",
            "phone": "0702030405",
            "phone_prefix_user": "+33",
            "password": "UneBelleLicorne!",
            "imgs_id": 2,
            "fonction": "Employee",
            "company_id": 2,  # ID d'une entreprise existante
            "permission_id": 2,  # Employee
            "statut":1
        },
        {
            "first_name": "Erwin",
            "last_name": "Smith",
            "email": "erwin.smith@example.com",
            "phone": "0803040506",
            "phone_prefix_user": "+33",
            "password": "ShinZuSasagewo!",
            "imgs_id": 3,
            "fonction": "Manager",
            "company_id": 2,
            "permission_id": 3,
            "statut":1
        },
        {
            "first_name": "Livaï",
            "last_name": "Ackerman",
            "email": "livai.ackerman@example.com",
            "phone": "0803040506",
            "phone_prefix_user": "+33",
            "password": "KENYYYYY!",
            "imgs_id": 3,
            "fonction": "Manager",
            "company_id": 2,
            "permission_id": 3,
            "statut":1
        },
        {
            "first_name": "Keisuke",
            "last_name": "Baji",
            "email": "keisuke.baji@example.com",
            "phone": "0803040506",
            "phone_prefix_user": "+33",
            "password": "1erDivisionToman!",
            "imgs_id": 3,
            "fonction": "Administrateur",
            "company_id": 2,
            "permission_id": 4,
            "statut":1
        },
        {
            "first_name": "Kenshin",
            "last_name": "Humura",
            "email": "kenshin.humura@example.com",
            "phone": "0803040506",
            "phone_prefix_user": "+33",
            "password": "Vagabon!",
            "imgs_id": 3,
            "fonction": "Employé ETNA",
            "company_id": 1,
            "permission_id": 5,
            "statut":1
        },
        {
            "first_name": "Jo",
            "last_name": "Togame",
            "email": "jo.togame@example.com",
            "phone": "0803040506",
            "phone_prefix_user": "+33",
            "password": "Kame-chan!",
            "imgs_id": 3,
            "fonction": "Employé ETNA",
            "company_id": 1,
            "permission_id": 5,
            "statut":1
        },
        {
            "first_name": "Suguru",
            "last_name": "Geto",
            "email": "suguru.geto@example.com",
            "phone": "0803040506",
            "phone_prefix_user": "+33",
            "password": "Spirale!",
            "imgs_id": 3,
            "fonction": "Manager ETNA",
            "company_id": 1,
            "permission_id": 6,
            "statut":1
        },
        {
            "first_name": "Satoru",
            "last_name": "Gojo",
            "email": "satoru.gojo@example.com",
            "phone": "0803040506",
            "phone_prefix_user": "+33",
            "password": "EquationImaginaireViolet!",
            "imgs_id": 3,
            "fonction": "Manager ETNA",
            "company_id": 1,
            "permission_id": 6,
            "statut":1
        },
        {
            "first_name": "Anne-Charlotte",
            "last_name": "Arnold",
            "email": "anne-charlotte.arnold@example.com",
            "phone": "0803040506",
            "phone_prefix_user": "+33",
            "password": "Valheriane!",
            "imgs_id": 3,
            "fonction": "AdminSUP",
            "company_id": 1,
            "permission_id": 7,
            "statut":1
        }
        # Ajoutez les autres utilisateurs ici...
    ]

    created_users = []

    with db.session.no_autoflush:  # Évite les conflits si des relations sont incomplètes
        for user_data in users_data:
            # Créer l'utilisateur
            user = Users(
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                email=user_data["email"],
                phone=user_data["phone"],
                phone_prefix_user=user_data["phone_prefix_user"],
                password=generate_password_hash(user_data["password"]),  # Hacher le mot de passe
                imgs_id=user_data["imgs_id"], 
                statut=user_data["statut"]
            )
            db.session.add(user)
            db.session.flush()  # Assure que l'ID utilisateur est généré

            # Créer l'entrée FonctionCompany
            fonction_company = FonctionCompany(
                company_id=user_data["company_id"],
                user_id=user.id_user,
                fonction=user_data["fonction"],
                permission_id=user_data["permission_id"]
            )
            db.session.add(fonction_company)

            # Générer une adresse pour l'utilisateur
            address = Address(
                address_line_1=fake.street_address(),
                address_line_2=fake.secondary_address(),
                city=fake.city(),
                postal_code=fake.postcode(),
                state_province=fake.state(),
                country=fake.country(),
                user_id=user.id_user,
                company_id=user_data["company_id"],
                is_billing=True
            )
            db.session.add(address)

            # Stocker les infos pour vérification ou debug
            created_users.append({
                "email": user_data["email"],
                "fonction": user_data["fonction"],
                "permission_id": user_data["permission_id"],
                "address": f"{address.address_line_1}, {address.city}, {address.country}"
            })

    # Valider les changements
    db.session.commit()
    print("Utilisateurs définis créés avec succès :")
    for user in created_users:
        print(f"Utilisateur : {user['email']}, Fonction : {user['fonction']}, Permission ID : {user['permission_id']}, Adresse : {user['address']}")

def populate_production_data():
    print("Peuplement des données pour la production...")
    
    # Appeler uniquement les fonctions nécessaires pour une base de production
    try:
        print("Peuplement des types d'images...")
        populate_type_imgs()

        print("Peuplement des images...")
        populate_default_images()

        print("Peuplement des modes de licence...")
        populate_license_modes()
        
        print("Peuplement des types d'offres...")
        populate_offer_types()
        
        print("Peuplement des permissions SSO...")
        populate_permissions_sso()
        
        print("Peuplement des droits d'accès...")
        populate_access_rights()

        print("Toutes les données pour la production ont été ajoutées.")
    except Exception as e:
        print(f"Erreur pendant le peuplement : {e}")
        
def populate_all(db):
    print("Récupération des données de base...")
        # Récupérer les autres données
    try:
        print("Peuplement des types d'images...")
        populate_type_imgs()

        print("Peuplement des images...")
        populate_images()
        images = db.session.query(Images).all()  # Récupérer les images pour les prochaines étapes

        print("Peuplement des utilisateurs...")
        populate_users(images)
        users = db.session.query(Users).all()  # Obtenir les utilisateurs

        print("Peuplement des entreprises...")
        populate_companies(images)
        companies = db.session.query(Company).all()  # Obtenir les entreprises

        print("Peuplement des adresses...")
        populate_addresses()
        addresses = db.session.query(Address).all()  # Obtenir les adresses

        print("Peuplement des produits...")
        populate_products()
        products = db.session.query(Product).all()  # Obtenir les produits

        print("Peuplement des associations produits-images...")
        populate_product_imgs()

        print("Peuplement des modes de licence...")
        populate_license_modes()

        print("Peuplement des droits d'accès...")
        populate_access_rights()
        
        print("Peuplement des types d'offres...")
        populate_offer_types()

        print("Peuplement des offres...")
        populate_offers()

        print("Peuplement des produits dans les offres...")
        populate_offer_products()

        print("Peuplement des configurations de produits...")
        populate_product_configurations()
     
        print("Peuplement des licences...")
        populate_licenses()

        print("Peuplement des permissions SSO...")
        populate_permissions_sso()

        print("Peuplement des fonctions...")
        populate_fonctions()

        print("Peuplement des moyens de paiement...")
        populate_payment_methods(users, companies, addresses) 

        print("Peuplement des historiques de connexion...")
        populate_login_history(users)

        print("Peuplement des fournisseurs OAuth...")
        populate_oauth_providers()
        oauth_providers = db.session.query(OAuthProvider).all()  # Obtenir les fournisseurs OAuth

        print("Peuplement des connexions OAuth utilisateur...")
        populate_user_oauth(users, oauth_providers)

        print("Peuplement des sessions utilisateur...")
        populate_user_sessions(users)

        print("Peuplement des logs de connexion...")
        populate_user_logs(users)

        print("Toutes les données ont été peuplées avec succès.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

def populate_all_hash(db):
    print("Récupération des données de base...")
        # Récupérer les autres données
    try:
        print("Peuplement des types d'images...")
        populate_type_imgs()

        print("Peuplement des images...")
        populate_images()
        images = db.session.query(Images).all()  # Récupérer les images pour les prochaines étapes

        print("Peuplement des utilisateurs...")
        populate_users_hash(images)
        users = db.session.query(Users).all()  # Obtenir les utilisateurs

        print("Peuplement des entreprises...")
        populate_companies(images)
        companies = db.session.query(Company).all()  # Obtenir les entreprises

        print("Peuplement des adresses...")
        populate_addresses()
        addresses = db.session.query(Address).all()  # Obtenir les adresses

        print("Peuplement des produits...")
        populate_products()
        products = db.session.query(Product).all()  # Obtenir les produits

        print("Peuplement des associations produits-images...")
        populate_product_imgs()

        print("Peuplement des modes de licence...")
        populate_license_modes()

        print("Peuplement des droits d'accès...")
        populate_access_rights()
        
        print("Peuplement des types d'offres...")
        populate_offer_types()

        print("Peuplement des offres...")
        populate_offers()

        print("Peuplement des produits dans les offres...")
        populate_offer_products()

        print("Peuplement des configurations de produits...")
        populate_product_configurations()
     
        print("Peuplement des licences...")
        populate_licenses()

        print("Peuplement des permissions SSO...")
        populate_permissions_sso()

        print("Peuplement des fonctions...")
        populate_fonctions()

        print("Peuplement des moyens de paiement...")
        populate_payment_methods(users, companies, addresses) 

        print("Peuplement des historiques de connexion...")
        populate_login_history(users)

        print("Peuplement des fournisseurs OAuth...")
        populate_oauth_providers()
        oauth_providers = db.session.query(OAuthProvider).all()  # Obtenir les fournisseurs OAuth

        print("Peuplement des connexions OAuth utilisateur...")
        populate_user_oauth(users, oauth_providers)

        print("Peuplement des sessions utilisateur...")
        populate_user_sessions(users)

        print("Peuplement des logs de connexion...")
        populate_user_logs(users)

        print("Toutes les données ont été peuplées avec succès.")


    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
               
def populate_products():
    for _ in range(random.randint(10, 20)):  # Générer entre 10 et 20 produits
        name = fake.word().capitalize()  # Nom du produit
        version = fake.word()  # Version (peut être quelque chose comme 'v1.0')
        product_type = fake.word().capitalize()  # Type du produit (par exemple 'Software', 'Tool')
        target_audience = fake.word().capitalize()  # Audience cible (par exemple 'Business', 'Developers')
        demo_link = fake.url()  # Lien vers une démo (facultatif)
        why_use = fake.paragraph()  # Pourquoi utiliser ce produit
        advantages = fake.paragraph()  # Avantages du produit
        description = fake.paragraph()  # Description du produit

        product = Product(
            name=name,
            version=version,
            type=product_type,
            target_audience=target_audience,
            demo_link=demo_link,
            why_use=why_use,
            advantages=advantages,
            description=description
        )
        
        db.session.add(product)

    db.session.commit()
    print(f"{random.randint(10, 20)} produits ajoutés.")

def populate_offers():
    # Récupérer quelques valeurs aléatoires des tables de référence
    offer_types = db.session.query(OfferTypes).all()
    license_modes = db.session.query(LicenseMode).all()
    access_rights = db.session.query(AccessRights).all()

    for _ in range(random.randint(10, 20)):  # Générer entre 10 et 20 offres
        offer_type = fake.random_element(offer_types)
        license_mode = fake.random_element(license_modes)
        access_right = fake.random_element(access_rights)

        offer_name = fake.word().capitalize()  # Nom de l'offre
        price = round(random.randint(1000, 5000) / 100, 2)  # Prix de l'offre, entre 10.00 et 50.00
        target_audience = fake.word().capitalize()  # Audience cible
        offer_advantages = fake.paragraph()  # Avantages de l'offre
        offer_duration = random.randint(1, 12)  # Durée de l'offre en mois, par exemple 6 mois
        created_at = fake.date_this_year()  # Date de création
        updated_at = fake.date_this_year()  # Date de mise à jour

        offer = Offer(
            offer_type_id=offer_type.id_offer_type,
            offer_name=offer_name,
            price=price,
            license_mode_id=license_mode.id_license_mode,
            target_audience=target_audience,
            offer_advantages=offer_advantages,
            offer_duration=offer_duration,
            created_at=created_at,
            updated_at=updated_at,
            access_rights_id=access_right.id_access_right
        )
        
        db.session.add(offer)

    db.session.commit()
    print(f"{random.randint(10, 20)} offres ajoutées.")
    
def populate_offer_products():
    # Récupérer toutes les offres et produits existants
    offers = db.session.query(Offer).all()
    products = db.session.query(Product).all()

    # Vérifier qu'il y a des données dans les deux tables
    if not offers or not products:
        print("Erreur: Pas assez de données dans les tables 'offers' ou 'products'")
        return

    for _ in range(random.randint(10, 20)):  # Générer entre 10 et 20 enregistrements
        offer = fake.random_element(offers)  # Sélectionner une offre aléatoire
        product = fake.random_element(products)  # Sélectionner un produit aléatoire

        # Vérifier si l'association existe déjà
        existing_relation = db.session.query(OfferProducts).filter_by(
            offer_id=offer.id_offer,
            product_id=product.id_product
        ).first()

        if existing_relation:
            print(f"Association déjà existante: Offer ID {offer.id_offer}, Product ID {product.id_product}")
            continue

        # Créer une nouvelle relation entre l'offre et le produit
        offer_product = OfferProducts(
            offer_id=offer.id_offer,
            product_id=product.id_product,
            access_count=random.randint(1, 10),  # Nombre d'accès aléatoire
            created_at=fake.date_this_year(),
            updated_at=fake.date_this_year()
        )

        db.session.add(offer_product)

    db.session.commit()
    print("Associations produits-offres ajoutées.")

def populate_images():
    # Récupérer tous les types d'images existants
    type_imgs = db.session.query(TypeImgs).all()

    # Vérifier qu'il y a des types d'images
    if not type_imgs:
        print("Erreur: Pas de types d'images disponibles")
        return

    for _ in range(random.randint(10, 20)):  # Créer entre 10 et 20 images
        type_img = fake.random_element(type_imgs)  # Sélectionner un type d'image aléatoire

        # Créer une nouvelle image avec une URL et une description
        image = Images(
            url=f"https://fakeimg.pl/350x200/?text={fake.word()}",
            type_imgs_id=type_img.id_type_img,
            description=fake.text(),
            created_at=fake.date_this_year(),
            updated_at=fake.date_this_year()
        )

        db.session.add(image)

    db.session.commit()
    print(f"{random.randint(10, 20)} images ajoutées.")
    
def populate_default_images():
    # Liste des images prédéfinies avec leurs URLs et descriptions
    predefined_images = [
        {
            "url": "https://example.com/logo_company.png",
            "description": "Logo par défaut pour les entreprises",
            "type_name": "Profile"
        },
        {
            "url": "https://example.com/default_product.png",
            "description": "Image par défaut pour les produits",
            "type_name": "Thumbnail"
        },
        {
            "url": "https://example.com/banner.png",
            "description": "Bannière par défaut",
            "type_name": "Banner"
        },
        {
            "url": "https://example.com/icon.png",
            "description": "Icône par défaut",
            "type_name": "Icon"
        }
    ]

    # Récupérer les types d'images existants dans la base
    type_imgs = {type_img.name: type_img for type_img in db.session.query(TypeImgs).all()}

    if not type_imgs:
        print("Erreur: Pas de types d'images disponibles")
        return

    new_images = []
    for img in predefined_images:
        # Vérifier si le type d'image associé existe
        if img["type_name"] not in type_imgs:
            print(f"Erreur: Le type d'image '{img['type_name']}' n'existe pas.")
            continue

        # Vérifier si l'image existe déjà dans la base
        existing_image = db.session.query(Images).filter_by(url=img["url"]).first()
        if existing_image:
            print(f"L'image avec l'URL '{img['url']}' existe déjà. Ignorée.")
            continue

        # Ajouter l'image à la base de données
        new_images.append(Images(
            url=img["url"],
            type_imgs_id=type_imgs[img["type_name"]].id_type_img,
            description=img["description"],
            created_at=fake.date_this_year(),
            updated_at=fake.date_this_year()
        ))

    # Insérer les nouvelles images dans la base de données
    if new_images:
        db.session.add_all(new_images)
        db.session.commit()
        print(f"{len(new_images)} images par défaut ajoutées.")
    else:
        print("Aucune nouvelle image ajoutée.")

def populate_product_imgs():
    # Récupérer tous les produits et les images existants
    products = db.session.query(Product).all()
    images = db.session.query(Images).all()

    # Vérifier qu'il y a des produits et des images dans la base de données
    if not products or not images:
        print("Erreur: Pas assez de produits ou d'images disponibles.")
        return

    associations_added = 0
    for _ in range(random.randint(10, 20)):  # Générer entre 10 et 20 associations
        product = fake.random_element(products)  # Sélectionner un produit aléatoire
        image = fake.random_element(images)  # Sélectionner une image aléatoire

        # Vérifier si l'association existe déjà
        existing_association = db.session.query(ProductImgs).filter_by(
            product_id=product.id_product,
            imgs_id=image.id_image
        ).first()

        if existing_association:
            continue  # Ignorer si l'association existe déjà

        # Créer une nouvelle association image-produit
        product_img = ProductImgs(
            product_id=product.id_product,
            imgs_id=image.id_image,
            primary_imgs=fake.boolean(),  # Déterminer si c'est l'image principale
            created_at=fake.date_this_year(),
            updated_at=fake.date_this_year()
        )

        db.session.add(product_img)
        associations_added += 1

    db.session.commit()
    print(f"{associations_added} associations produit-image ajoutées.")

def populate_product_configurations():
    # Récupérer tous les produits existants
    products = db.session.query(Product).all()

    # Vérifier qu'il y a des produits
    if not products:
        print("Erreur: Pas de produits disponibles.")
        return

    for _ in range(random.randint(10, 20)):  # Créer entre 10 et 20 configurations de produits
        product = random.choice(products)  # Sélectionner un produit aléatoire

        # Créer une configuration produit avec des informations aléatoires
        config = ProductConfigurations(
            product_id=product.id_product,
            config_type=random.randint(1, 5),  # Type de configuration aléatoire
            operating_system=fake.random_element(["Windows", "MacOS", "Linux"]),
            processor=fake.random_element(["Intel i5", "Intel i7", "AMD Ryzen 5", "AMD Ryzen 7"]),
            ram=fake.random_element(["8GB", "16GB", "32GB"]),
            storage=fake.random_element(["256GB SSD", "512GB SSD", "1TB HDD"]),
            gpu=fake.random_element(["NVIDIA GTX 1650", "AMD Radeon RX 580", "Intel Integrated Graphics"]),
            internet_connection=fake.random_element(["Ethernet", "WiFi", "5G"]),
            supported_browsers=fake.random_element(["Chrome, Firefox", "Edge, Safari", "Chrome, Safari"]),
            created_at=fake.date_this_year(),
            updated_at=fake.date_this_year()
        )

        db.session.add(config)

    db.session.commit()
    print(f"{random.randint(10, 20)} configurations produits ajoutées.")

def populate_licenses():
    print(f"Je suis dans la fonction licences")
    # Récupérer tous les utilisateurs, entreprises, produits et modes de licence existants
    users = db.session.query(Users).all()
    companies = db.session.query(Company).all()
    products = db.session.query(Product).all()
    license_modes = db.session.query(LicenseMode).all()
    access_rights = db.session.query(AccessRights).all()

    # Vérifier qu'il y a des utilisateurs, entreprises, produits et modes de licences
    if not users or not companies or not products or not license_modes or not access_rights:
        print("Erreur: Pas assez de données pour peupler les licences.")
        return

    for _ in range(random.randint(10, 20)):  # Générer entre 10 et 20 licences
        user = fake.random_element(users)
        company = fake.random_element(companies)
        product = fake.random_element(products)
        license_mode = fake.random_element(license_modes)
        access_right = fake.random_element(access_rights)

        # Créer une nouvelle licence avec des données aléatoires
        license = License(
            company_id=company.id_company,
            user_id=user.id_user,
            product_id=product.id_product,
            license_mode_id=license_mode.id_license_mode,
            start_date=fake.date_this_year(),
            end_date=fake.date_this_year(),
            created_at=fake.date_this_year(),
            updated_at=fake.date_this_year(),
            active=fake.boolean(),
            access_rights_id=access_right.id_access_right
        )

        db.session.add(license)

    db.session.commit()
    print(f"{random.randint(20, 40)} licences ajoutées.")

def populate_users(images):
    # Liste de mots pour les mots de passe faciles
    easy_password_words = [
        # Animaux
        "Lion", "Tiger", "Eagle", "Dolphin", "Panda", "Zebra", 
        "Phoenix", "Wolf", "Fox", "Hawk", "Shark", "Dragon",

        # Villes
        "Paris", "Berlin", "Tokyo", "Rome", "Sydney", "Kyoto", 
        "Osaka", "Hiroshima", "Nagasaki", "Sapporo", "NewYork", "London",

        # Personnages d'anime
        "Naruto", "Luffy", "Goku", "Sakura", "Eren", "Mikasa", 
        "Levi", "Hinata", "Asuna", "Kirito", "Rukia", "Yato"
    ]

    # Table des préfixes téléphoniques par pays
    country_prefixes = {
        "FR": "+33",
        "US": "+1",
        "DE": "+49"
    }

    for _ in range(random.randint(20, 0)):
        while True:
            email = fake.unique.email()
            if not db.session.query(Users).filter_by(email=email).first():
                break

        # Génération d'un préfixe téléphonique aléatoire
        country_code = fake.random_element(list(country_prefixes.keys()))
        phone_prefix = country_prefixes.get(country_code, "+1")  # Préfixe par défaut : +1

        # Génération d'un mot de passe facile
        word = random.choice(easy_password_words)
        number = random.randint(10, 99)  # Ajouter un nombre entre 10 et 99
        raw_password = f"{word}{number}"

        user = Users(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=email,
            phone=fake.phone_number(),
            phone_prefix_user=phone_prefix,  # Stocker le préfixe dans le champ dédié
            password=raw_password,  # Stocker le mot de passe en clair pour les tests
            imgs_id=random.choice(images).id_image,
            created_at=fake.date_this_year(),
            updated_at=fake.date_this_year(), 
            statut=random.randint(1,3)
        )

        print(f"Utilisateur créé : {email}, Mot de passe : {raw_password}, Préfixe : {phone_prefix}")  # Affiche les infos pour le test

        db.session.add(user)

    db.session.commit()
    print("Utilisateurs ajoutés.")
    
def populate_users_hash(images):
    # Liste de mots pour les mots de passe faciles
    easy_password_words = [
        # Animaux
        "Lion", "Tiger", "Eagle", "Dolphin", "Panda", "Zebra", 
        "Phoenix", "Wolf", "Fox", "Hawk", "Shark", "Dragon",

        # Villes
        "Paris", "Berlin", "Tokyo", "Rome", "Sydney", "Kyoto", 
        "Osaka", "Hiroshima", "Nagasaki", "Sapporo", "NewYork", "London",

        # Personnages d'anime
        "Naruto", "Luffy", "Goku", "Sakura", "Eren", "Mikasa", 
        "Levi", "Hinata", "Asuna", "Kirito", "Rukia", "Yato"
    ]

    # Table des préfixes téléphoniques par pays
    country_prefixes = {
        "FR": "+33",
        "US": "+1",
        "DE": "+49"
    }

    for _ in range(random.randint(20, 40)):
        while True:
            email = fake.unique.email()
            if not db.session.query(Users).filter_by(email=email).first():
                break

        # Génération d'un préfixe téléphonique aléatoire
        country_code = fake.random_element(list(country_prefixes.keys()))
        phone_prefix = country_prefixes.get(country_code, "+1")  # Préfixe par défaut : +1

        # Génération d'un mot de passe facile
        word = random.choice(easy_password_words)
        number = random.randint(10, 99)  # Ajouter un nombre entre 10 et 99
        raw_password = f"{word}{number}"
        hashed_password = generate_password_hash(raw_password)  # Hacher le mot de passe

        user = Users(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=email,
            phone=fake.phone_number(),
            phone_prefix_user=phone_prefix,  # Préfixe unique pour chaque utilisateur
            password=hashed_password,  # Mot de passe haché
            imgs_id=random.choice(images).id_image,
            created_at=fake.date_this_year(),
            updated_at=fake.date_this_year(),
            statut=random.randint(1,3)
        )

        print(f"Utilisateur créé : {email}, Mot de passe : {raw_password}")  # Affiche les infos pour le test

        db.session.add(user)

    db.session.commit()
    print("Utilisateurs ajoutés.")

# Fonction pour peupler la table Company
def populate_companies(images):
    # Dictionnaire pour les préfixes téléphoniques en fonction des codes pays
    country_prefixes = {
        "FR": "+33",
        "US": "+1",
        "DE": "+49"
    }

    # Étape 1 : Ajouter l'entreprise ETNA Sea Robots
    etna_company = Company(
        id_company=1,  # Spécifie l'ID souhaité
        name_company="ETNA Sea Robots",
        imgs_id=random.choice(images).id_image,  # Associe une image aléatoire pour cet exemple
        email_company="contact@etna-searobots.com",
        company_phone="+33 1234567890",  # Numéro de téléphone fictif
        phone_prefix_company="+33",
        created_at=fake.date_this_year(),
        updated_at=fake.date_this_year(),
        national_id="1234567890",
        registry_type="SIRET",
        country_code="FR",
        website="https://www.etna-searobots.com"
    )

    # Ajoute ETNA à la session
    db.session.add(etna_company)

    # Étape 2 : Générer d'autres entreprises
    for _ in range(random.randint(10, 20)):  # Créer entre 10 et 20 entreprises
        while True:
            email_company = fake.unique.company_email()
            if not db.session.query(Company).filter_by(email_company=email_company).first():
                break
        
        # Générer un code pays aléatoire
        country_code = fake.random_element(list(country_prefixes.keys()))
        phone_prefix = country_prefixes[country_code]  # Obtenir le préfixe basé sur le code pays

        company = Company(
            name_company=fake.company(),
            imgs_id=random.choice(images).id_image,  # Utiliser l'image passée en paramètre
            email_company=email_company,
            company_phone=f"{phone_prefix} {fake.msisdn()[:10]}",  # Combiner le préfixe et un numéro de téléphone
            phone_prefix_company=phone_prefix,  # Stocker le préfixe dans le champ dédié
            created_at=fake.date_this_year(),
            updated_at=fake.date_this_year(),
            national_id=fake.random_number(digits=10),
            registry_type=fake.random_element(["SIRET", "EIN", "VAT"]),
            country_code=country_code,
            website=fake.url()
        )
        db.session.add(company)

    # Enregistrer tous les changements dans la base de données
    db.session.commit()
    print("Entreprises ajoutées avec préfixes téléphoniques.")


def populate_permissions_sso():
    permissions = [ "Viewer" ,"Employee","Manager", "Admin","Employee-Etna","Manager-Etna","Admin-Etna"]
    
    # Récupérer les permissions existantes en utilisant le champ `permission_name`
    existing_permissions = {perm.permission_name for perm in db.session.query(PermissionSSO).all()}
    
    # Créer les nouvelles permissions si elles n'existent pas déjà
    new_permissions = [
        PermissionSSO(
            permission_name=name,
            permission_description=f"Description of {name}"
        )
        for name in permissions if name not in existing_permissions
    ]

    # Ajouter et valider les nouvelles permissions
    if new_permissions:
        db.session.add_all(new_permissions)
        db.session.commit()
        print(f"{len(new_permissions)} permissions SSO ajoutées.")
    else:
        print("Toutes les permissions SSO existent déjà.")


# Fonction pour peupler la table FonctionCompany
def populate_fonctions():
    # Récupérer les entreprises existantes
    companies = db.session.query(Company).all()
    # Récupérer les utilisateurs existants
    users = db.session.query(Users).all()
    # Récupérer la permission 1
    default_permission = db.session.query(PermissionSSO).filter(PermissionSSO.id_permission == 1).first()
    # Récupérer les permissions 2, 3, et 4
    other_permissions = db.session.query(PermissionSSO).filter(PermissionSSO.id_permission.in_([2, 3, 4])).all()

    # Vérifications initiales
    if not companies or not users or not default_permission or len(other_permissions) < 3:
        print("Erreur: Il faut des utilisateurs, des entreprises, et les permissions 1, 2, 3 et 4.")
        return

    for user in users:
        if random.random() < 0.25:  # 40% des utilisateurs n'auront pas d'entreprise
            company_id = None
            permission = default_permission  # Assigner la permission 1
        else:
            company = random.choice(companies)
            company_id = company.id_company
            permission = random.choice(other_permissions)  # Permission aléatoire parmi 2, 3, ou 4

        # Créer une entrée pour la fonction de l'utilisateur dans la table FonctionCompany
        fonction = FonctionCompany(
            company_id=company_id,
            user_id=user.id_user,
            fonction=fake.job(),  # Rôle ou fonction de l'utilisateur dans l'entreprise
            permission_id=permission.id_permission
        )

        db.session.add(fonction)

    db.session.commit()
    print(f"{len(users)} fonctions ajoutées.")


def populate_addresses():
    users = db.session.query(Users).all()  # Récupérer les utilisateurs existants
    companies = db.session.query(Company).all()  # Récupérer les entreprises existantes

    if not users and not companies:
        print("Erreur: Pas d'utilisateurs ni d'entreprises disponibles.")
        return

    for _ in range(random.randint(10, 20)):  # Créer entre 10 et 20 adresses
        address = Address(
            address_line_1=fake.street_address(),
            address_line_2=fake.secondary_address(),
            city=fake.city(),
            postal_code=fake.zipcode(),
            state_province=fake.state(),
            country=fake.country(),
            user_id=random.choice(users).id_user if random.randint(0, 1) else None,  # Lier à un utilisateur ou une entreprise
            company_id=random.choice(companies).id_company  if random.randint(0, 1) else None,  # Lier à une entreprise
            invoice_date=fake.date_this_year(),
            is_billing=True,  # Marquer comme adresse de facturation par défaut
            address_type=random.randint(1, 3),  # Type d'adresse (1: domicile, 2: entreprise, 3: autre)
        )
        db.session.add(address)

    db.session.commit()
    print(f"{random.randint(10, 20)} adresses ajoutées.")

def populate_payment_methods(users, companies, addresses):
    payment_methods = []
    for _ in range(random.randint(10, 20)):
        user = random.choice(users) if random.random() < 0.5 else None
        company = random.choice(companies) if random.random() >= 0.5 else None
        provider = random.choice(['Visa', 'Mastercard', 'PayPal', 'Stripe'])
        payment_type = random.choice(['Carte bancaire', 'PayPal', 'Stripe', 'Virement bancaire'])
        last_four_digits = str(random.randint(1000, 9999))
        expiration_date = fake.date_this_century(before_today=True, after_today=False)
        billing_address = random.choice(addresses) if random.random() < 0.5 else None
        is_active = random.choice([True, False])
        
        payment_method = PaymentMethod(
            user_id=user.id_user if user else None,
            company_id=company.id_company if company else None,
            provider=provider,
            payment_type=payment_type,
            last_four_digits=last_four_digits,
            expiration_date=expiration_date,
            billing_address_id=billing_address.id_address if billing_address else None,
            is_active=is_active
        )
        payment_methods.append(payment_method)
    
    db.session.add_all(payment_methods)
    db.session.commit()

import random
def populate_license_modes():
    # Liste des noms de modes de licence
    license_mode_names = [
        'Abonnement',
        'Achat unique',
        'Essai gratuit',
        'Licence perpétuelle',
        'Pay-per-use',
        'Licence temporaire',
        'Location de licence'
    ]
    
    # Récupérer les noms existants dans la base de données
    existing_names = {license_mode.name for license_mode in db.session.query(LicenseMode).all()}
    
    # Générer un nombre aléatoire de modes à créer (entre 10 et 20)
    new_license_modes = []
    for _ in range(random.randint(10, 20)):
        name = random.choice(license_mode_names)
        if name not in existing_names:
            new_license_modes.append(LicenseMode(name=name))
            existing_names.add(name)  # Mettre à jour pour éviter les doublons dans la boucle
    
    # Ajouter tous les nouveaux modes de licence à la base de données
    if new_license_modes:
        db.session.add_all(new_license_modes)
        db.session.commit()
        print(f"{len(new_license_modes)} nouveaux modes de licence ajoutés.")
    else:
        print("Tous les modes de licence existent déjà. Aucun ajout nécessaire.")

def populate_offer_types():
    offer_types = []
    for _ in range(random.randint(10, 20)):
        name = random.choice(['Promotion', 'Essai gratuit', 'Réduction', 'Offre spéciale'])
        
        offer_type = OfferTypes(
            name=name
        )
        offer_types.append(offer_type)
    
    db.session.add_all(offer_types)
    db.session.commit()

def populate_access_rights():
    access_right_names = ['Admin', 'User', 'Manager', 'Viewer']
    existing_rights = {right.name for right in db.session.query(AccessRights).all()}
    new_rights = [
        AccessRights(name=name, description=fake.sentence(nb_words=6)) 
        for name in access_right_names if name not in existing_rights
    ]

    if new_rights:
        db.session.add_all(new_rights)
        db.session.commit()
        print(f"{len(new_rights)} droits d'accès ajoutés.")
    else:
        print("Tous les droits d'accès existent déjà.")

def populate_type_imgs():
    """Peuple la table type_imgs avec une liste fixe de types d'images."""
    type_names = ['Profile', 'Banner', 'Thumbnail', 'Icon', 'Cover']
    
    # Vérifier si les types d'images existent déjà (évite les doublons)
    existing_names = {type_img.name for type_img in db.session.query(TypeImgs).all()}
    
    new_type_imgs = []
    for name in type_names:
        if name not in existing_names:
            new_type_imgs.append(TypeImgs(name=name))
    
    if new_type_imgs:
        db.session.add_all(new_type_imgs)
        db.session.commit()
        print(f"{len(new_type_imgs)} types d'images ajoutés à la table type_imgs.")
    else:
        print("Tous les types d'images existent déjà. Aucun ajout nécessaire.")

def populate_login_history( users):
    login_history = []
    for _ in range(random.randint(10, 20)):
        user = random.choice(users)
        login_time = fake.date_this_year(before_today=True, after_today=False)
        logout_time = login_time + timedelta(hours=random.randint(1, 5))  # Connexion pendant 1 à 5 heures
        ip_address = fake.ipv4()  # Générer une adresse IPv4 aléatoire
        device_info = fake.user_agent()  # Générer un agent utilisateur aléatoire
        
        login_entry = LoginHistory(
            user_id=user.id_user,
            login_time=login_time,
            logout_time=logout_time,
            ip_address=ip_address,
            device_info=device_info
        )
        
        login_history.append(login_entry)
    
    db.session.add_all(login_history)
    db.session.commit()

def populate_oauth_providers():
    oauth_providers = []
    for _ in range(random.randint(10, 20)):
        provider_name = random.choice(['Google', 'Facebook', 'GitHub', 'Twitter', 'LinkedIn'])
        client_id = fake.uuid4()
        client_secret = fake.uuid4()
        redirect_uri = fake.url()

        oauth_provider = OAuthProvider(
            provider_name=provider_name,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri
        )

        oauth_providers.append(oauth_provider)

    db.session.add_all(oauth_providers)
    db.session.commit()

def populate_user_oauth( users, oauth_providers):
    user_oauths = []
    for _ in range(random.randint(10, 20)):
        user = random.choice(users)
        oauth_provider = random.choice(oauth_providers)
        provider_user_id = fake.uuid4()  # Un identifiant unique de l'utilisateur pour le fournisseur
        access_token = fake.uuid4()
        refresh_token = fake.uuid4()
        access_token_expiration = fake.date_this_year()
        refresh_token_expiration = access_token_expiration + timedelta(days=30)  # Le refresh token expire dans 30 jours

        user_oauth = UserOAuth(
            user_id=user.id_user,
            provider_id=oauth_provider.id_oauth_provider,
            provider_user_id=provider_user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expiration=access_token_expiration,
            refresh_token_expiration=refresh_token_expiration
        )

        user_oauths.append(user_oauth)

    db.session.add_all(user_oauths)
    db.session.commit()

def populate_user_sessions( users):
    user_sessions = []
    for _ in range(random.randint(10, 20)):
        user = random.choice(users)
        session_token = fake.uuid4()  # Générer un jeton de session unique
        created_at = fake.date_this_year(before_today=True, after_today=False)
        expires_at = created_at + timedelta(days=random.randint(1, 7))  # Expire entre 1 et 7 jours après la création

        user_session = UserSession(
            user_id=user.id_user,
            session_token=session_token,
            created_at=created_at,
            expires_at=expires_at
        )

        user_sessions.append(user_session)

    db.session.add_all(user_sessions)
    db.session.commit()
    
def populate_user_logs(users):
    user_logs = []
    for _ in range(random.randint(10, 20)):
        user = random.choice(users)
        action = random.choice([
            "Connexion réussie",
            "Déconnexion",
            "Modification du mot de passe",
            "Mise à jour du profil",
            "Ajout d'une adresse",
            "Suppression d'une adresse",
            "Ajout d'un moyen de paiement",
            "Suppression d'un moyen de paiement"
        ])
        ip_address = fake.ipv4()  # Générer une adresse IP aléatoire
        user_navweb = random.choice(["Chrome", "Firefox", "Edge", "Safari", "Opera"])
        created_at = fake.date_this_year(before_today=True, after_today=False)

        user_log = LogUserAction(
            user_id=user.id_user,
            action=action,
            ip_address=ip_address,
            user_navweb=user_navweb,
            created_at=created_at
        )

        user_logs.append(user_log)

    db.session.add_all(user_logs)
    db.session.commit()
    print(f"{len(user_logs)} logs utilisateur ajoutés.")












