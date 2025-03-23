#from urllib import request
from flask import request
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from models import License, db, AccessRights
from schemas import AccessRightsSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
import jwt
from app import check_permissions
from decorators import role_required
from marshmallow import ValidationError

access_right_ns = Namespace('access_rights', description='Access rights and role management')


@access_right_ns.route('/<int:access_right_id>')
class AccessRightsResource(Resource):
    # Initialiser les schémas
    access_rights_schema = AccessRightsSchema()
    access_rights_list_schema = AccessRightsSchema(many=True)
    access_rights_patch_schema = AccessRightsSchema(partial=True)

    @jwt_required()
    @role_required(1)  # Exemple : accès pour les utilisateurs avec un rôle >= 2
    def get(self, access_right_id=None):
        """Récupère un droit d'accès spécifique ou tous les droits d'accès."""
        if access_right_id:
            access_right = AccessRights.query.get_or_404(access_right_id)
            return self.access_rights_schema.dump(access_right), 200

        all_access_rights = AccessRights.query.all()
        return self.access_rights_list_schema.dump(all_access_rights), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def post(self):
        """Crée un nouveau droit d'accès."""
        try:
            new_access_right_data = self.access_rights_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        new_access_right = AccessRights(**new_access_right_data)
        db.session.add(new_access_right)
        db.session.commit()
        return self.access_rights_schema.dump(new_access_right), 201

    @jwt_required()
    @role_required(6)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def put(self, access_right_id):
        """Remplace complètement un droit d'accès existant."""
        access_right = AccessRights.query.get_or_404(access_right_id)

        try:
            updated_access_right_data = self.access_rights_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_access_right_data.items():
            setattr(access_right, key, value)

        db.session.commit()
        return self.access_rights_schema.dump(access_right), 200

    @jwt_required()
    @role_required(6)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def patch(self, access_right_id):
        """Met à jour partiellement un droit d'accès."""
        access_right = AccessRights.query.get_or_404(access_right_id)

        try:
            updated_access_right_data = self.access_rights_patch_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_access_right_data.items():
            if value is not None:
                setattr(access_right, key, value)

        db.session.commit()
        return self.access_rights_schema.dump(access_right), 200

    @jwt_required()
    @role_required(6)  # Exemple : accès pour les utilisateurs avec un rôle >= 6 (Admin)
    def delete(self, access_right_id):
        """Supprime un droit d'accès, sauf s'il est utilisé dans des licences."""
        access_right = AccessRights.query.get_or_404(access_right_id)

        # Vérifier si ce droit d'accès est utilisé dans des licences
        licenses_using_access = License.query.filter_by(access_right_id=access_right_id).all()

        if licenses_using_access:
            # Renvoyer la liste des licences qui utilisent ce droit d'accès
            return {
                "message": "Impossible de supprimer ce droit d'accès car il est utilisé.",
                "licenses": [
                    {
                        "id_license": license.id_license,
                        "user_id": license.user_id,
                        "user_name": f"{license.user.first_name} {license.user.last_name}" if license.user else None,
                        "company_id": license.company_id,
                        "company_name": license.company.name_company if license.company else None,
                        "product_id": license.product_id,
                        "product_name": license.product.name if license.product else None,
                        "active": license.active
                    }
                    for license in licenses_using_access
                ]
            }, 400  # Erreur de requête

        # Si aucune licence ne l'utilise, suppression
        db.session.delete(access_right)
        db.session.commit()
        return {"message": "Droit d'accès supprimé avec succès"}, 204



