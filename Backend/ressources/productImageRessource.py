#from urllib import request
from flask import request
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
import jwt

from decorators import role_required
from models import db,ProductImgs
from schemas import ProductImgsSchema


product_image_ns = Namespace('product_images', description='Images associated with products')


@product_image_ns.route('/<int:product_image_id>')
class ProductImageResource(Resource):
    # Initialiser les schémas
    product_image_schema = ProductImgsSchema()
    product_image_list_schema = ProductImgsSchema(many=True)
    product_image_patch_schema = ProductImgsSchema(partial=True)

    #@jwt_required()
    #@role_required(0)  # Exemple : accès pour les utilisateurs avec un rôle >= 2
    def get(self, product_image_id=None):
        """Récupère une association produit-image spécifique ou toutes les associations."""     
        parser = reqparse.RequestParser()
        parser.add_argument('imgs_id', type=int, location='args')
        parser.add_argument('product_id', type=int, location='args')
        args = parser.parse_args()
        
        imgs_id = args.get('imgs_id')
        product_id = args.get('product_id')
        
        query = ProductImgs.query
        if product_image_id:
            product_image = ProductImgs.query.get_or_404(product_image_id)
            return self.product_image_schema.dump(product_image), 200
        if imgs_id is not None:
            query = query.filter_by(imgs_id=imgs_id)
        if product_id is not None:
            query = query.filter_by(product_id=product_id)
            
        filtered_product_images = query.all()
        if not filtered_product_images:
            return {"message": "No offers match the given criteria"}, 404
        
        return self.product_image_list_schema.dump(filtered_product_images), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def post(self):
        """Crée une nouvelle relation produit-image."""
        try:
            new_product_img_data = self.product_image_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        # Vérifie si une relation existe déjà avec la même combinaison product_id et imgs_id
        existing_relation = ProductImgs.query.filter_by(
            product_id=new_product_img_data["product_id"],
            imgs_id=new_product_img_data["imgs_id"]
        ).first()

        if existing_relation:
            return {
                "message": "La relation entre ce produit et cette image existe déjà."
            }, 409  # Conflit HTTP

        # Crée une nouvelle relation si elle n'existe pas encore
        new_product_img = ProductImgs(**new_product_img_data)
        db.session.add(new_product_img)
        db.session.commit()

        return self.product_image_schema.dump(new_product_img), 201


    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def put(self, product_image_id):
        """Remplace complètement une association produit-image existante."""
        product_image = ProductImgs.query.get_or_404(product_image_id)

        try:
            updated_product_image_data = self.product_image_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_product_image_data.items():
            setattr(product_image, key, value)

        db.session.commit()
        return self.product_image_schema.dump(product_image), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def patch(self, product_image_id):
        """Met à jour partiellement une association produit-image."""
        product_image = ProductImgs.query.get_or_404(product_image_id)

        try:
            updated_product_image_data = self.product_image_patch_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_product_image_data.items():
            if value is not None:
                setattr(product_image, key, value)

        db.session.commit()
        return self.product_image_schema.dump(product_image), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 4 (Admin)
    def delete(self, product_image_id):
        """Supprime une association produit-image."""
        product_image = ProductImgs.query.get_or_404(product_image_id)
        db.session.delete(product_image)
        db.session.commit()
        return {"message": "Association produit-image supprimée avec succès"}, 204
