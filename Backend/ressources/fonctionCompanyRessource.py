#from urllib import request
from flask import request
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
import jwt

from models import db,FonctionCompany
from schemas import FonctionCompanySchema

company_function_ns = Namespace('company_functions', description='Functions and roles in a company')


@company_function_ns.route('/<int:fonction_id>')
class FonctionCompanyResource(Resource):
    # Initialiser les schémas
    fonction_company_schema = FonctionCompanySchema()
    fonction_company_list_schema = FonctionCompanySchema(many=True)
    fonction_company_patch_schema = FonctionCompanySchema(partial=True)

    @jwt_required()
    #@role_required(2)  # Exemple : accès pour les utilisateurs avec un rôle >= 2
    def get(self, fonction_id=None):
        """Récupère une fonction spécifique ou toutes les fonctions avec des filtres facultatifs."""
        parser = reqparse.RequestParser()
        parser.add_argument('company_id', type=int, location='args')
        parser.add_argument('user_id', type=int, location='args')
        parser.add_argument('permission_id', type=int, location='args')
        args = parser.parse_args()

        company_id = args.get('company_id')
        user_id = args.get('user_id')
        permission_id = args.get('permission_id')

        # Si un ID spécifique de fonction est fourni
        if fonction_id:
            fonction = FonctionCompany.query.get_or_404(fonction_id, description="Fonction non trouvée")
            return self.fonction_company_schema.dump(fonction), 200

        # Construire la requête avec des filtres facultatifs
        query = FonctionCompany.query
        if company_id is not None:
            query = query.filter_by(company_id=company_id)
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        if permission_id is not None:
            query = query.filter_by(permission_id=permission_id)

        # Récupérer les résultats filtrés
        filtered_fonctions = query.all()
        if not filtered_fonctions:
            return {"message": "Aucune fonction ne correspond aux critères donnés"}, 404

        return self.fonction_company_list_schema.dump(filtered_fonctions), 200


    @jwt_required()
    #@role_required(3)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def post(self):
        """Crée une nouvelle fonction dans une entreprise."""
        try:
            new_fonction_data = self.fonction_company_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        new_fonction = FonctionCompany(**new_fonction_data)
        db.session.add(new_fonction)
        db.session.commit()
        return self.fonction_company_schema.dump(new_fonction), 201

    @jwt_required()
    #@role_required(3)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def put(self, fonction_id):
        """Remplace complètement une fonction existante."""
        fonction = FonctionCompany.query.get_or_404(fonction_id)

        try:
            updated_fonction_data = self.fonction_company_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_fonction_data.items():
            setattr(fonction, key, value)

        db.session.commit()
        return self.fonction_company_schema.dump(fonction), 200

    @jwt_required()
    #@role_required(3)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def patch(self, fonction_id):
        """Met à jour partiellement une fonction existante."""
        fonction = FonctionCompany.query.get_or_404(fonction_id)

        try:
            updated_fonction_data = self.fonction_company_patch_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_fonction_data.items():
            if value is not None:
                setattr(fonction, key, value)

        db.session.commit()
        return self.fonction_company_schema.dump(fonction), 200

    @jwt_required()
    #@role_required(4)  # Exemple : accès pour les utilisateurs avec un rôle >= 4
    def delete(self, fonction_id):
        """Supprime une fonction d'une entreprise."""
        fonction = FonctionCompany.query.get_or_404(fonction_id)
        db.session.delete(fonction)
        db.session.commit()
        return {"message": "Fonction supprimée avec succès"}, 204
