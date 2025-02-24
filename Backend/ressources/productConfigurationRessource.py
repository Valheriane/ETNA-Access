#from urllib import request
from flask import request
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from decorators import role_required
from models import db, ProductConfigurations
from schemas import ProductConfigurationSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
import jwt

product_config_ns = Namespace('product_configurations', description='Configurations for products')


@product_config_ns.route('/<int:config_id>')
class ProductConfigurationResource(Resource):
    # Initialiser les schémas
    product_config_schema = ProductConfigurationSchema()
    product_config_list_schema = ProductConfigurationSchema(many=True)
    product_config_patch_schema = ProductConfigurationSchema(partial=True)

    #@jwt_required()
    #@role_required(2)  # Exemple : accès pour les utilisateurs avec un rôle >= 2
    def get(self, config_id=None):
        """Récupère une configuration produit spécifique ou toutes les configurations."""
        parser = reqparse.RequestParser()
        parser.add_argument('product_id', type=int, location='args')
        args = parser.parse_args()
        
        product_id = args.get('product_id')
        query = ProductConfigurations.query
        
        if config_id:
            product_config = ProductConfigurations.query.get_or_404(config_id)
            return self.product_config_schema.dump(product_config), 200
        if product_id is not None:
            query = query.filter_by(product_id=product_id)

        filtered_product_config = query.all()
        if not filtered_product_config:
            return {"message": "No offers match the given criteria"}, 404
        return self.product_config_list_schema.dump(filtered_product_config), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def post(self):
        """Crée une nouvelle configuration produit."""
        try:
            new_product_config_data = self.product_config_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        new_product_config = ProductConfigurations(**new_product_config_data)
        db.session.add(new_product_config)
        db.session.commit()
        return self.product_config_schema.dump(new_product_config), 201

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def put(self, config_id):
        """Remplace complètement une configuration produit existante."""
        product_config = ProductConfigurations.query.get_or_404(config_id)

        try:
            updated_product_config_data = self.product_config_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_product_config_data.items():
            setattr(product_config, key, value)

        db.session.commit()
        return self.product_config_schema.dump(product_config), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def patch(self, config_id):
        """Met à jour partiellement une configuration produit."""
        product_config = ProductConfigurations.query.get_or_404(config_id)

        try:
            updated_product_config_data = self.product_config_patch_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_product_config_data.items():
            if value is not None:
                setattr(product_config, key, value)

        db.session.commit()
        return self.product_config_schema.dump(product_config), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 4
    def delete(self, config_id):
        """Supprime une configuration produit."""
        product_config = ProductConfigurations.query.get_or_404(config_id)
        db.session.delete(product_config)
        db.session.commit()
        return {"message": "Configuration produit supprimée avec succès"}, 204




