from ressources.userPermissionFullRessource import UserPermissionFullResource
from ressources.oAuthProviderRessource import  OAuthProviderRessource, oauth_provider_ns
from ressources.userOAuthRessource import UserOAuthListResource, UserOAuthResource, user_oauth_ns
from ressources.accessRightRessource import AccessRightsResource, access_right_ns
from ressources.addressRessource import AddressResource, address_ns
from ressources.companyRessource import CompanyResource, company_ns
from ressources.fonctionCompanyRessource import FonctionCompanyResource, company_function_ns
from ressources.imageRessource import ImageResource, image_ns
from ressources.licenceModeRessource import LicenseModeResource, licence_mode_ns
from ressources.licenceRessource import LicenseResource, licence_ns
from ressources.logUserActionRessource import LogUserActionResource, log_user_action_ns
from ressources.loginHistoryRessource import LoginHistoryResource, login_history_ns
from ressources.offerProductRessource import OfferProductResource, offer_product_ns
from ressources.offerRessource import OfferResource, offer_ns
from ressources.offerTypeRessource import OfferTypeResource, offer_type_ns
from ressources.paymentRessource import PaymentMethodResource, payment_ns
from ressources.permissionRessource import PermissionSSOResource, permission_ns
from ressources.productConfigurationRessource import ProductConfigurationResource, product_config_ns
from ressources.productImageRessource import ProductImageResource, product_image_ns
from ressources.productRessource import ProductResource, product_ns
from ressources.typeImgRessource import TypeImgsResource, image_type_ns
from ressources.userRessource import UserResource, user_ns
from ressources.userSessionRessource import UserSessionListResource, UserSessionResource, user_session_ns

from app import app  # Importer l'application depuis app.py
from flask import render_template, request, jsonify
#from flask_restful import Api
from flask_restx import Api, Resource
from models import Users, db  # Assurez-vous que vos modèles sont importés correctement
from werkzeug.security import check_password_hash
from flask_jwt_extended import JWTManager, create_access_token

# Gestion des OPTIONS pour CORS
'''
@app.route('/handle_options', methods=['OPTIONS'])
def handle_options():
    response = jsonify()
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Access-Control-Allow-Origin')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS, GET, PUT, DELETE, PATCH')
    return response
'''



api = Api(app, doc='/docs', title='My API', version='1.0', description='Documentation de l\'API')

api.add_namespace(user_ns)
api.add_namespace(company_ns)
api.add_namespace(payment_ns)
api.add_namespace(oauth_provider_ns)
api.add_namespace(user_oauth_ns)
api.add_namespace(access_right_ns)
api.add_namespace(company_function_ns)
api.add_namespace(image_ns)
api.add_namespace(licence_mode_ns)
api.add_namespace(address_ns)
api.add_namespace(licence_ns)
api.add_namespace(log_user_action_ns)
api.add_namespace(login_history_ns)
api.add_namespace(offer_product_ns)
api.add_namespace(offer_ns)
api.add_namespace(offer_type_ns)
api.add_namespace(permission_ns)
api.add_namespace(product_config_ns)
api.add_namespace(product_image_ns)
api.add_namespace(product_ns)
api.add_namespace(image_type_ns)
api.add_namespace(user_session_ns)


@app.route('/login', methods=['POST'])
def login():
    """Authentifie un utilisateur et renvoie un token d'accès."""
    # Récupérer les données du corps de la requête
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Vérifier l'utilisateur en base de données
    user = Users.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    # Créer un objet pour stocker les informations nécessaires dans le token
    identity = {
        "id_user": user.id_user,
        "first_name": user.first_name,
        # On récupère la première permission ou la permission la plus élevée si plusieurs fonctions
        "permissions": user.fonctions[0].permission_id if user.fonctions else None,
        "company_id": user.fonctions[0].company_id if user.fonctions else None  # Associe l'entreprise si existante
    }

    # Générer un token d'accès
    access_token = create_access_token(identity=identity)

    # Construire la réponse
    response = {
        "access_token": access_token,
        "user_id": user.id_user,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "permissions": identity["permissions"],
        "company_id": identity["company_id"]
    }

    return jsonify(response), 200



@app.route("/")
def home():
    return render_template("index.html")


@app.route('/check-jwt', methods=['GET'])
def check_jwt():
    return jsonify({"JWT_SECRET_KEY": app.config['JWT_SECRET_KEY']})

@api.route('/test')
class TestResource(Resource):  # Ajoutez l'héritage de Resource
    def get(self):
        return {'message': 'Hello, world!'}


#Class ressource simple
api.add_resource(UserResource, '/users', '/users/<int:user_id>')
api.add_resource(CompanyResource, '/companies', '/companies/<int:company_id>')
api.add_resource(ProductResource, '/products', '/products/<int:product_id>')
api.add_resource(OfferResource, '/offers', '/offers/<int:offer_id>')
api.add_resource(ImageResource, '/images', '/images/<int:image_id>')
api.add_resource(LicenseResource, '/licenses', '/licenses/<int:license_id>')
api.add_resource(PermissionSSOResource, '/permissions', '/permissions/<int:permission_id>')
api.add_resource(AddressResource, '/addresses', '/addresses/<int:address_id>')
api.add_resource(PaymentMethodResource, '/payment_methods', '/payment_methods/<int:payment_method_id>')
api.add_resource(LicenseModeResource, '/license_modes', '/license_modes/<int:license_mode_id>')
api.add_resource(OfferTypeResource, '/offer_types', '/offer_types/<int:offer_type_id>')
api.add_resource(AccessRightsResource, '/access_rights', '/access_rights/<int:access_right_id>')
api.add_resource(TypeImgsResource, '/type_imgs', '/type_imgs/<int:type_img_id>')
api.add_resource(LoginHistoryResource, '/login_history', '/login_history/<int:login_history_id>')
api.add_resource(OAuthProviderRessource, '/oauth_providers', '/oauth_providers/<int:oauth_provider_id>')
api.add_resource(UserOAuthListResource, '/user_oauths')  # Liste des connexions OAuth
api.add_resource(UserOAuthResource, '/user_oauths/<int:user_oauth_id>')  # Détail d'une connexion OAuth
api.add_resource(UserSessionListResource, '/user_sessions')
api.add_resource(UserSessionResource, '/user_sessions/<int:user_session_id>')
api.add_resource(LogUserActionResource, '/log_user_actions', '/log_user_actions/<int:log_user_action_id>')

#Classe type OnetoMany

#Class ressource Has
api.add_resource(OfferProductResource, '/offer-products', '/offer-products/<int:offer_product_id>')
api.add_resource(ProductImageResource, '/product-images', '/product-images/<int:product_image_id>')
api.add_resource(ProductConfigurationResource, '/product-configurations', '/product-configurations/<int:config_id>')
# Routes pour les fonctions des entreprises
api.add_resource(FonctionCompanyResource, '/fonctions', '/fonctions/<int:fonction_id>')

#Class complexe
# Définition de la route pour la création d'un utilisateur avec permissions
api.add_resource(UserPermissionFullResource, '/api/users/full')



# Point d'entrée de l'application
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5050, debug=True)
