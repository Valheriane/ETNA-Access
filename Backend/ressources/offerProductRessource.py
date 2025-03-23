#from urllib import request
from flask import request
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from decorators import role_required
from models import db, OfferProducts
from schemas import OfferProductSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
import jwt

offer_product_ns = Namespace('offer_products', description='Products included in offers')


@offer_product_ns.route('/<int:offer_product_id>')
class OfferProductResource(Resource):
    # Initialiser les schémas
    offer_product_schema = OfferProductSchema()
    offer_product_list_schema = OfferProductSchema(many=True)
    offer_product_patch_schema = OfferProductSchema(partial=True)

    #jwt_required()
    #@role_required(2)  # Exemple : accès pour les utilisateurs avec un rôle >= 2
    def get(self, offer_product_id=None):
        """Récupère une association produit-offre spécifique ou toutes les associations."""
        parser = reqparse.RequestParser()
        parser.add_argument('offer_id', type=int, location='args')
        parser.add_argument('product_id', type=int, location='args')
        args = parser.parse_args()
        
        offer_id = args.get('offer_id')
        product_id = args.get('product_id')
        
        query = OfferProducts.query
        if offer_product_id:
            offer_product = OfferProducts.query.get_or_404(offer_product_id, description="Offer not found")
            return self.offer_product_schema.dump(offer_product), 200
        if offer_id is not None:
            query = query.filter_by(offer_id=offer_id)
        if product_id is not None:
            query = query.filter_by(product_id=product_id)
            
        filtered_offers = query.all()
        if not filtered_offers:
            return {"message": "No offers match the given criteria"}, 404
        
        return self.offer_product_list_schema.dump(filtered_offers), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def post(self):
        """Crée une nouvelle association produit-offre."""
        try:
            new_offer_product_data = self.offer_product_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        # Vérifie si l'association existe déjà (clé unique sur offer_id et product_id)
        existing_offer_product = OfferProducts.query.filter_by(
            offer_id=new_offer_product_data['offer_id'],
            product_id=new_offer_product_data['product_id']
        ).first()

        if existing_offer_product:
            return {"message": "Cette association offre-produit existe déjà."}, 409

        new_offer_product = OfferProducts(**new_offer_product_data)
        db.session.add(new_offer_product)
        db.session.commit()
        return self.offer_product_schema.dump(new_offer_product), 201

    @jwt_required()
    @role_required(5) # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def put(self, offer_product_id):
        """Remplace complètement une association produit-offre existante."""
        offer_product = OfferProducts.query.get_or_404(offer_product_id)

        try:
            updated_offer_product_data = self.offer_product_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_offer_product_data.items():
            setattr(offer_product, key, value)

        db.session.commit()
        return self.offer_product_schema.dump(offer_product), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def patch(self, offer_product_id):
        """Met à jour partiellement une association produit-offre."""
        offer_product = OfferProducts.query.get_or_404(offer_product_id)

        try:
            updated_offer_product_data = self.offer_product_patch_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_offer_product_data.items():
            if value is not None:
                setattr(offer_product, key, value)

        db.session.commit()
        return self.offer_product_schema.dump(offer_product), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 4 (Admin)
    def delete(self, offer_product_id):
        """Supprime une association produit-offre."""
        offer_product = OfferProducts.query.get_or_404(offer_product_id)
        db.session.delete(offer_product)
        db.session.commit()
        return {"message": "Association produit-offre supprimée avec succès"}, 204



