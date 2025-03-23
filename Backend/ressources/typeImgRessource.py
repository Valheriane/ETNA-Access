#from urllib import request
from flask import request
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from decorators import role_required
from models import db, TypeImgs
from schemas import TypeImgsSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
import jwt

image_type_ns = Namespace('image_types', description='Types of images (e.g., icons, thumbnails)')


@image_type_ns.route('/<int:type_img_id>')
class TypeImgsResource(Resource):
    # Initialiser les schémas
    type_imgs_schema = TypeImgsSchema()
    type_imgs_list_schema = TypeImgsSchema(many=True)
    type_imgs_patch_schema = TypeImgsSchema(partial=True)

    @jwt_required()
    @role_required(1)  # Exemple : accès pour les utilisateurs avec un rôle >= 2
    def get(self, type_img_id=None):
        """Récupère un type d'image spécifique ou tous les types d'images."""
        if type_img_id:
            type_img = TypeImgs.query.get_or_404(type_img_id)
            return self.type_imgs_schema.dump(type_img), 200

        all_type_imgs = TypeImgs.query.all()
        return self.type_imgs_list_schema.dump(all_type_imgs), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def post(self):
        """Crée un nouveau type d'image."""
        try:
            new_type_img_data = self.type_imgs_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        new_type_img = TypeImgs(**new_type_img_data)
        db.session.add(new_type_img)
        db.session.commit()
        return self.type_imgs_schema.dump(new_type_img), 201

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def put(self, type_img_id):
        """Remplace complètement un type d'image existant."""
        type_img = TypeImgs.query.get_or_404(type_img_id)

        try:
            updated_type_img_data = self.type_imgs_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_type_img_data.items():
            setattr(type_img, key, value)

        db.session.commit()
        return self.type_imgs_schema.dump(type_img), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def patch(self, type_img_id):
        """Met à jour partiellement un type d'image."""
        type_img = TypeImgs.query.get_or_404(type_img_id)

        try:
            updated_type_img_data = self.type_imgs_patch_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_type_img_data.items():
            if value is not None:
                setattr(type_img, key, value)

        db.session.commit()
        return self.type_imgs_schema.dump(type_img), 200

    @jwt_required()
    @role_required(7)  # Exemple : accès pour les utilisateurs avec un rôle >= 4 (Admin)
    def delete(self, type_img_id):
        """Supprime un type d'image."""
        type_img = TypeImgs.query.get_or_404(type_img_id)
        db.session.delete(type_img)
        db.session.commit()
        return {"message": "Type d'image supprimé avec succès"}, 204


