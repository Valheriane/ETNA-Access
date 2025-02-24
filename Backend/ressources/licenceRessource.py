#from urllib import request
from flask import request
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from models import db, License
from schemas import LicenseSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
import jwt

licence_ns = Namespace('licences', description='Licence management for products')

@licence_ns.route('/<int:license_id>')
class LicenseResource(Resource):
     
    # Initialiser les schémas
    license_schema = LicenseSchema()
    license_list_schema = LicenseSchema(many=True)
    license_patch_schema = LicenseSchema(partial=True)

    @jwt_required()
    #@role_required(2)  # Exemple : accès pour les utilisateurs avec un rôle >= 2
    def get(self, license_id=None):
        """Récupère une licence spécifique ou toutes les licences avec des filtres.""" 
        # Parser pour extraire les filtres de la requête
        parser = reqparse.RequestParser()
        parser.add_argument('company_id', type=int, location='args')
        parser.add_argument('user_id', type=int, location='args')
        parser.add_argument('product_id', type=int, location='args')
        parser.add_argument('license_mode_id', type=int, location='args')
        parser.add_argument('access_rights_id', type=int, location='args')
        args = parser.parse_args()
        
        # Extraire les filtres
        company_id = args.get('company_id')
        user_id = args.get('user_id')
        product_id = args.get('product_id')
        license_mode_id = args.get('license_mode_id')
        access_rights_id = args.get('access_rights_id')

        # Commencer la requête
        query = License.query

        # Filtrage par licence spécifique si un ID de licence est fourni
        if license_id:
            license = License.query.get_or_404(license_id)
            return self.license_schema.dump(license), 200
        
        # Appliquer les filtres si les arguments sont présents
        if company_id is not None:
            query = query.filter_by(company_id=company_id)
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        if product_id is not None:
            query = query.filter_by(product_id=product_id)
        if license_mode_id is not None:
            query = query.filter_by(license_mode_id=license_mode_id)
        if access_rights_id is not None:
            query = query.filter_by(access_rights_id=access_rights_id)

        # Exécuter la requête filtrée
        filtered_licenses = query.all()

        # Si aucun résultat n'est trouvé
        if not filtered_licenses:
            return {"message": "No licenses match the given criteria"}, 404

        # Retourner les résultats filtrés
        return self.license_list_schema.dump(filtered_licenses), 200

    @jwt_required()
    #@role_required(3)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def post(self):
        """Crée une nouvelle licence."""
        try:
            new_license_data = self.license_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        new_license = License(**new_license_data)
        db.session.add(new_license)
        db.session.commit()
        return self.license_schema.dump(new_license), 201

    @jwt_required()
    #@role_required(3)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def put(self, license_id):
        """Remplace complètement une licence existante."""
        license = License.query.get_or_404(license_id)

        try:
            updated_license_data = self.license_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_license_data.items():
            setattr(license, key, value)

        db.session.commit()
        return self.license_schema.dump(license), 200

    @jwt_required()
    #@role_required(3)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def patch(self, license_id):
        """Met à jour partiellement une licence."""
        license = License.query.get_or_404(license_id)

        try:
            updated_license_data = self.license_patch_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_license_data.items():
            if value is not None:
                setattr(license, key, value)

        db.session.commit()
        return self.license_schema.dump(license), 200

    @jwt_required()
    #@role_required(4)  # Exemple : accès pour les utilisateurs avec un rôle >= 4
    def delete(self, license_id):
        """Supprime une licence."""
        license = License.query.get_or_404(license_id)
        db.session.delete(license)
        db.session.commit()
        return {"message": "Licence supprimée avec succès"}, 204

