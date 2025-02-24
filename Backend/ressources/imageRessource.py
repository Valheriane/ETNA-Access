#from urllib import request
from flask import request
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from decorators import role_required
from models import Company, ProductImgs, Users, db, Images
from schemas import ImageSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
import jwt

image_ns = Namespace('images', description='General image management')

@image_ns.route('/<int:image_id>')
class ImageResource(Resource):
     
    # Initialiser les schémas
    image_schema = ImageSchema()
    image_list_schema = ImageSchema(many=True)
    image_patch_schema = ImageSchema(partial=True)

    #@jwt_required()
    #@role_required(2)  # Exemple : accès pour les utilisateurs avec un rôle >= 2
    def get(self, image_id=None):
        """Récupère une image spécifique ou toutes les images."""
        parser = reqparse.RequestParser()
        parser.add_argument('type_imgs_id', type=int, location='args')
        args = parser.parse_args()
        type_imgs_id = args.get('type_imgs_id')
        
        if image_id:
            image = Images.query.get_or_404(image_id)
            return self.image_schema.dump(image), 200
        
        query = Images.query
        if type_imgs_id is not None:
            query = query.filter_by(type_imgs_id=type_imgs_id)
            
        filtered_images = query.all()
        if not filtered_images:
            return {"message": "No offers match the given criteria"}, 404
        
        #all_images = Images.query.all()
        return self.image_list_schema.dump(filtered_images), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def post(self):
        """Crée une nouvelle image."""
        try:
            new_image_data = self.image_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        # Créer une nouvelle instance d'image
        new_image = Images(**new_image_data)
        db.session.add(new_image)
        db.session.commit()
        return self.image_schema.dump(new_image), 201

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def put(self, image_id):
        """Remplace complètement une image existante."""
        image = Images.query.get_or_404(image_id)

        try:
            updated_image_data = self.image_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_image_data.items():
            setattr(image, key, value)

        db.session.commit()
        return self.image_schema.dump(image), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def patch(self, image_id):
        """Met à jour partiellement une image."""
        image = Images.query.get_or_404(image_id)

        try:
            updated_image_data = self.image_patch_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_image_data.items():
            if value is not None:
                setattr(image, key, value)

        db.session.commit()
        return self.image_schema.dump(image), 200

    @jwt_required()
    @role_required(5)  # Accès restreint aux admins (>=5)
    def delete(self, image_id):
        """Supprime une image après vérification qu'elle n'est pas utilisée."""  

        image = Images.query.get_or_404(image_id)

        # Vérifier si l'image est utilisée dans Company, User ou ProductImgs
        is_used_in_company = db.session.query(Company).filter_by(imgs_id=image_id).first()
        is_used_in_user = db.session.query(Users).filter_by(imgs_id=image_id).first()
        is_used_in_product = db.session.query(ProductImgs).filter_by(imgs_id=image_id).first()

        # Générer un message de précision avec les détails
        usage_details = []

        if is_used_in_company:
            usage_details.append(f"Utilisée dans l'entreprise ID: {is_used_in_company.id_company}, Nom: {is_used_in_company.name_company}.")
        if is_used_in_user:
            usage_details.append(f"Utilisée par l'utilisateur ID: {is_used_in_user.id_user}, Nom: {is_used_in_user.first_name}.")
        if is_used_in_product:
            product_name = is_used_in_product.product.name  # Accéder au nom du produit
            usage_details.append(f"Utilisée dans le produit ID: {is_used_in_product.product.id_product}, Nom: {product_name}.")


        if usage_details:
            return {"message": f"Impossible de supprimer l'image : elle est encore utilisée dans les endroits suivants : {', '.join(usage_details)}."}, 400

        # Suppression de l'image si elle n'est référencée nulle part
        db.session.delete(image)
        db.session.commit()

        return {"message": "Image supprimée avec succès"}, 204






