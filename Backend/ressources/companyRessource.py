#from urllib import request
from flask import request
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from app import check_permissions
from decorators import role_required
from models import Address, FonctionCompany, License, db, Company, PaymentMethod
from schemas import CompanySchema
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
import jwt

company_ns = Namespace('companies', description='Operations related to companies')


@company_ns.route('/<int:company_id>')
class CompanyResource(Resource):
     
    # Initialiser les schémas
    company_schema = CompanySchema()
    company_list_schema = CompanySchema(many=True)
    company_patch_schema = CompanySchema(partial=True)

    @jwt_required()
    @role_required(2)  # Rôle minimal pour accéder aux entreprises
    def get(self, company_id=None):
        """Récupère une entreprise spécifique ou toutes les entreprises avec filtre sur imgs_id."""

        # Extraire les informations du token JWT
        claims = get_jwt_identity()
        user_id_from_token = claims.get("id_user")
        user_permission = claims.get("permissions")
        company_id_from_token = claims.get("company_id")

        # Initialiser le parser pour les arguments
        parser = reqparse.RequestParser()
        parser.add_argument('imgs_id', type=int, location='args')
        args = parser.parse_args()

        # Récupérer le filtre sur les images
        imgs_id = args.get('imgs_id')

        # Si une entreprise spécifique est demandée
        if company_id:
            company = Company.query.get_or_404(company_id, description="Company not found")

            # **Renforcement des restrictions**
            if user_permission < 5 and company.id_company != company_id_from_token:
                return {"message": "Accès refusé : vous ne pouvez voir que votre propre entreprise."}, 403

            return self.company_schema.dump(company), 200

        # Construire une requête avec des filtres
        query = Company.query

        # Filtrer par imgs_id si nécessaire
        if imgs_id is not None:
            query = query.filter_by(imgs_id=imgs_id)

        # Appliquer les restrictions pour les permissions 2, 3 et 4
        if user_permission in [2, 3, 4]:
            query = query.filter_by(id_company=company_id_from_token)  # Ne voir que sa propre entreprise

        # Récupérer les résultats
        filtered_companies = query.all()

        if not filtered_companies:
            return {"message": "No companies match the given criteria"}, 404

        return self.company_list_schema.dump(filtered_companies), 200



    @jwt_required()
    @role_required(1)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def post(self):
        """Crée une nouvelle entreprise."""
        try:
            new_company_data = self.company_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        new_company = Company(**new_company_data)
        db.session.add(new_company)
        db.session.commit()
        return self.company_schema.dump(new_company), 201

    @jwt_required()
    @role_required(4)  # Accès pour les utilisateurs avec un rôle >= 4
    def put(self, company_id):
        """Remplace complètement une entreprise existante."""

        # Extraire les informations du token JWT
        claims = get_jwt_identity()
        user_permission = claims.get("permissions")
        company_id_from_token = claims.get("company_id")

        # Récupérer l'entreprise demandée
        company = Company.query.get_or_404(company_id, description="Company not found")

        # **Restriction : un user de permission 4 ne peut modifier que sa propre entreprise**
        if user_permission == 4 and company.id_company != company_id_from_token:
            return {"message": "Accès refusé : vous ne pouvez modifier que votre propre entreprise."}, 403

        try:
            updated_company_data = self.company_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        # Appliquer les modifications
        for key, value in updated_company_data.items():
            setattr(company, key, value)

        db.session.commit()
        return self.company_schema.dump(company), 200


    @jwt_required()
    @role_required(4)  # Accès pour les utilisateurs avec un rôle >= 4
    def patch(self, company_id):
        """Met à jour partiellement une entreprise."""

        # Extraire les informations du token JWT
        claims = get_jwt_identity()
        user_permission = claims.get("permissions")
        company_id_from_token = claims.get("company_id")

        # Récupérer l'entreprise demandée
        company = Company.query.get_or_404(company_id, description="Company not found")

        # **Restriction : un user de permission 4 ne peut modifier que sa propre entreprise**
        if user_permission == 4 and company.id_company != company_id_from_token:
            return {"message": "Accès refusé : vous ne pouvez modifier que votre propre entreprise."}, 403

        try:
            updated_company_data = self.company_patch_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        # Appliquer les modifications partielles
        for key, value in updated_company_data.items():
            if value is not None:
                setattr(company, key, value)

        db.session.commit()
        return self.company_schema.dump(company), 200


    @jwt_required()
    @role_required(5)  # Seuls les utilisateurs avec un rôle >= 5 peuvent supprimer une entreprise
    def delete(self, company_id):
        """Supprime une entreprise après vérifications de sécurité."""

        # Vérifier si l'entreprise existe
        company = Company.query.get_or_404(company_id, description="Company not found")

        # Définition des relations bloquantes avec récupération des entités liées
        blocking_relations = {
            "fonctions associées": FonctionCompany.query.filter_by(company_id=company_id).all(),
            "moyens de paiement": PaymentMethod.query.filter_by(company_id=company_id).all(),
            "adresses": Address.query.filter_by(company_id=company_id).all(),
            "licences": License.query.filter_by(company_id=company_id).all(),
        }

        # Vérifier si au moins une relation existe
        for key, entities in blocking_relations.items():
            if entities:
                details = [
                    f"(ID: {getattr(e, 'id_fonction_company', getattr(e, 'id_address', getattr(e, 'id_payment_method', getattr(e, 'id_license', 'N/A'))))}, "
                    f"Nom: {getattr(e, 'name', getattr(e, 'fonction', getattr(e, 'address_line_1', 'N/A')))} )"
                    for e in entities
                ]
                
                return {
                    "message": f"Impossible de supprimer cette entreprise : des {key} sont encore associés. Détails: {', '.join(details)}"
                }, 403


        # Suppression sécurisée
        db.session.delete(company)
        db.session.commit()
        return {"message": "Entreprise supprimée avec succès"}, 204





