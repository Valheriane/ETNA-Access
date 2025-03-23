#from urllib import request
from flask import request
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from decorators import role_required
from models import db, PermissionSSO
from schemas import PermissionSSOSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
import jwt

permission_ns = Namespace('permissions', description='Permissions management')


@permission_ns.route('/<int:permission_id>')
class PermissionSSOResource(Resource):
     
    # Initialiser les schémas
    permission_sso_schema = PermissionSSOSchema()
    permission_sso_list_schema = PermissionSSOSchema(many=True)
    permission_sso_patch_schema = PermissionSSOSchema(partial=True)

    @jwt_required()
    @role_required(1)  # Minimum requis pour accéder à une permission spécifique
    def get(self, permission_id=None):
        """Récupère une permission spécifique ou toutes les permissions en fonction du niveau d'autorisation."""

        current_user_role = get_jwt_identity().get("permissions", 0)  # Récupère le rôle, avec défaut 0

        if permission_id:
            # Vérifie si l'utilisateur a le droit d'accéder à une permission spécifique
            permission = PermissionSSO.query.get_or_404(permission_id)

            if current_user_role >= 5:
                return self.permission_sso_schema.dump(permission), 200
            elif current_user_role == 4 and 2 <= permission.id_permission <= 4:
                return self.permission_sso_schema.dump(permission), 200
            elif 1 <= current_user_role <= 3 and 1 <= permission.id_permission <= 3:
                return self.permission_sso_schema.dump(permission), 200
            else:
                return {"message": "Vous n'avez pas l'autorisation de voir cette permission."}, 403

        # Si aucune permission spécifique n'est demandée, on ne change pas cette partie
        if current_user_role >= 5:
            all_permissions = PermissionSSO.query.all()
        elif current_user_role == 4:
            all_permissions = PermissionSSO.query.filter(PermissionSSO.id_permission.between(2, 4)).all()
        else:
            return {"message": "Vous n'avez pas l'autorisation de voir cette liste."}, 403

        return self.permission_sso_list_schema.dump(all_permissions), 200




    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def post(self):
        """Crée une nouvelle permission."""
        try:
            new_permission_data = self.permission_sso_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        new_permission = PermissionSSO(**new_permission_data)
        db.session.add(new_permission)
        db.session.commit()
        return self.permission_sso_schema.dump(new_permission), 201

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def put(self, permission_id):
        """Remplace complètement une permission existante."""
        permission = PermissionSSO.query.get_or_404(permission_id)

        try:
            updated_permission_data = self.permission_sso_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_permission_data.items():
            setattr(permission, key, value)

        db.session.commit()
        return self.permission_sso_schema.dump(permission), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def patch(self, permission_id):
        """Met à jour partiellement une permission."""
        permission = PermissionSSO.query.get_or_404(permission_id)

        try:
            updated_permission_data = self.permission_sso_patch_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_permission_data.items():
            if value is not None:
                setattr(permission, key, value)

        db.session.commit()
        return self.permission_sso_schema.dump(permission), 200

    @jwt_required()
    @role_required(7)  # Exemple : accès pour les utilisateurs avec un rôle >= 4
    def delete(self, permission_id):
        """Supprime une permission."""
        permission = PermissionSSO.query.get_or_404(permission_id)
        db.session.delete(permission)
        db.session.commit()
        return {"message": "Permission supprimée avec succès"}, 204
