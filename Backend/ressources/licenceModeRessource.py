#from urllib import request
from flask import request
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from models import License, db, LicenseMode
from schemas import LicenseModeSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
import jwt
from app import check_permissions
from decorators import role_required
from marshmallow import ValidationError


licence_mode_ns = Namespace('licence_modes', description='Modes of licences (subscription, purchase, etc.)')


@licence_mode_ns.route('/<int:license_mode_id>')
class LicenseModeResource(Resource):
    # Initialiser les schémas
    license_mode_schema = LicenseModeSchema()
    license_mode_list_schema = LicenseModeSchema(many=True)
    license_mode_patch_schema = LicenseModeSchema(partial=True)

    #@jwt_required()
    #@role_required(1)  # Exemple : accès pour les utilisateurs avec un rôle >= 2
    def get(self, license_mode_id=None):
        """Récupère un mode de licence spécifique ou tous les modes de licence."""
        if license_mode_id:
            license_mode = LicenseMode.query.get_or_404(license_mode_id)
            return self.license_mode_schema.dump(license_mode), 200

        all_license_modes = LicenseMode.query.all()
        return self.license_mode_list_schema.dump(all_license_modes), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def post(self):
        """Crée un nouveau mode de licence."""
        try:
            new_license_mode_data = self.license_mode_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        new_license_mode = LicenseMode(**new_license_mode_data)
        db.session.add(new_license_mode)
        db.session.commit()
        return self.license_mode_schema.dump(new_license_mode), 201

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def put(self, license_mode_id):
        """Remplace complètement un mode de licence existant."""
        license_mode = LicenseMode.query.get_or_404(license_mode_id)

        try:
            updated_license_mode_data = self.license_mode_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_license_mode_data.items():
            setattr(license_mode, key, value)

        db.session.commit()
        return self.license_mode_schema.dump(license_mode), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def patch(self, license_mode_id):
        """Met à jour partiellement un mode de licence."""
        license_mode = LicenseMode.query.get_or_404(license_mode_id)

        try:
            updated_license_mode_data = self.license_mode_patch_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_license_mode_data.items():
            if value is not None:
                setattr(license_mode, key, value)

        db.session.commit()
        return self.license_mode_schema.dump(license_mode), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 5 (Admin)
    def delete(self, license_mode_id):
        """Supprime un mode de licence, sauf s'il est utilisé dans des licences."""
        license_mode = LicenseMode.query.get_or_404(license_mode_id)

        # Vérifier si ce mode de licence est utilisé dans des licences
        licenses_using_mode = License.query.filter_by(license_mode_id=license_mode_id).all()

        if licenses_using_mode:
            # Renvoyer la liste des licences qui utilisent ce mode de licence
            return {
                "message": "Impossible de supprimer ce mode de licence car il est utilisé.",
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
                    for license in licenses_using_mode
                ]

            }, 400  # Erreur de requête

        # Si aucune licence ne l'utilise, suppression
        db.session.delete(license_mode)
        db.session.commit()
        return {"message": "Mode de licence supprimé avec succès"}, 204





