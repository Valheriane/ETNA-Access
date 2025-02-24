#from urllib import request
from flask import request
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from decorators import role_required
from models import db, Product
from schemas import ProductSchema
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import bcrypt
import jwt


product_ns = Namespace('offers', description='Operations related to products')


@product_ns.route('/<int:product_id>')
class ProductResource(Resource):
     
    # Initialiser les schémas
    product_schema = ProductSchema()
    product_list_schema = ProductSchema(many=True)
    product_patch_schema = ProductSchema(partial=True)
    
    #@jwt_required()
    #@role_required(2)  # Exemple : accès pour les utilisateurs avec un rôle >= 2
    def get(self, product_id=None):
        """Récupère un produit spécifique ou tous les produits."""
        if product_id:
            product = Product.query.get_or_404(product_id)
            if not product:
                return {"message": "Cet élément n'existe pas."}, 404
            return self.product_schema.dump(product), 200  # Utilisation de self.product_schema
        
        all_products = Product.query.all()
        return self.product_list_schema.dump(all_products), 200  # Utilisation de self.product_list_schema

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 2
    def post(self):
        """Crée un nouveau produit."""
        try:
            # Valider et charger les données du JSON en tant que dictionnaire
            new_product_data = self.product_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        # Créer un nouveau produit de manière explicite
        new_product = Product(
            name=new_product_data['name'],
            version=new_product_data['version'],
            type=new_product_data['type'],
            target_audience=new_product_data['target_audience'],
            demo_link=new_product_data['demo_link'],
            why_use=new_product_data['why_use'],
            advantages=new_product_data['advantages'],
            description=new_product_data['description'],
            #created_at=datetime.now(),  # Remplir la date de création avec la date actuelle
            #updated_at=datetime.now(),  # Remplir la date de mise à jour avec la date actuelle
        )
        
        # Ajouter le produit à la base de données
        db.session.add(new_product)
        db.session.commit()

        # Retourner les données du produit créé avec le schéma
        return self.product_schema.dump(new_product), 201  # Utilisation de self.product_schema


    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def put(self, product_id):
        """Remplace complètement un produit existant."""
        product = Product.query.get_or_404(product_id)
        
        try:
            updated_product_data = self.product_schema.load(request.json)  # Utilisation de self.product_schema
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400
        
        for key, value in updated_product_data.items():
            setattr(product, key, value)
        
        db.session.commit()
        return self.product_schema.dump(product), 200  # Utilisation de self.product_schema

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def patch(self, product_id):
        """Met à jour partiellement un produit."""
        product = Product.query.get_or_404(product_id)
        
        try:
            updated_product_data = self.product_patch_schema.load(request.json)  # Utilisation de self.product_patch_schema
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400
        
        for key, value in updated_product_data.items():
            if value is not None:
                setattr(product, key, value)
        
        db.session.commit()
        return self.product_schema.dump(product), 200  # Utilisation de self.product_schema

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 4 (Admin)
    def delete(self, product_id):
        """Supprime un produit."""
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return {"message": "Produit supprimé avec succès"}, 204



