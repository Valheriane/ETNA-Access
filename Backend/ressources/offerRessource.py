#from urllib import request
from flask import request
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from decorators import role_required
from models import db, Offer
from schemas import OfferSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
import jwt

offer_ns = Namespace('offers', description='Operations related to offers')


@offer_ns.route('/<int:offer_id>')
class OfferResource(Resource):
     
    # Initialiser les schémas
    offer_schema = OfferSchema()
    offer_list_schema = OfferSchema(many=True)
    offer_patch_schema = OfferSchema(partial=True)

    #@jwt_required()
    #@role_required(2)  # Exemple : accès pour les utilisateurs avec un rôle >= 2
    def get(self, offer_id=None):
        """Récupère une offre spécifique ou toutes les offres avec des filtres facultatifs."""
        # Initialiser le parser pour les arguments
        parser = reqparse.RequestParser()
        parser.add_argument('offer_type_id', type=int, location='args')
        parser.add_argument('license_mode_id', type=int, location='args')
        parser.add_argument('access_rights_id', type=int, location='args')
        args = parser.parse_args()

        # Récupérer les valeurs des arguments
        offer_type_id = args.get('offer_type_id')
        license_mode_id = args.get('license_mode_id')
        access_rights_id = args.get('access_rights_id')

        # Vérifier si un ID spécifique d'offre est demandé
        if offer_id:
            offer = Offer.query.get_or_404(offer_id, description="Offer not found")
            return self.offer_schema.dump(offer), 200

        # Construire une requête avec des filtres dynamiques
        query = Offer.query
        if offer_type_id is not None:
            query = query.filter_by(offer_type_id=offer_type_id)
        if license_mode_id is not None:
            query = query.filter_by(license_mode_id=license_mode_id)
        if access_rights_id is not None:
            query = query.filter_by(access_rights_id=access_rights_id)

        # Récupérer les résultats filtrés
        filtered_offers = query.all()
        if not filtered_offers:
            return {"message": "No offers match the given criteria"}, 404

        # Retourner les données filtrées
        return self.offer_list_schema.dump(filtered_offers), 200

    @jwt_required()
    @role_required(5) # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def post(self):
        """Crée une nouvelle offre."""
        try:
            new_offer_data = self.offer_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        new_offer = Offer(**new_offer_data)
        db.session.add(new_offer)
        db.session.commit()
        return self.offer_schema.dump(new_offer), 201

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def put(self, offer_id):
        """Remplace complètement une offre existante."""
        offer = Offer.query.get_or_404(offer_id)

        try:
            updated_offer_data = self.offer_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_offer_data.items():
            setattr(offer, key, value)

        db.session.commit()
        return self.offer_schema.dump(offer), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    def patch(self, offer_id):
        """Met à jour partiellement une offre."""
        offer = Offer.query.get_or_404(offer_id)

        try:
            updated_offer_data = self.offer_patch_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_offer_data.items():
            if value is not None:
                setattr(offer, key, value)

        db.session.commit()
        return self.offer_schema.dump(offer), 200

    @jwt_required()
    @role_required(5) # Exemple : accès pour les utilisateurs avec un rôle >= 4 (Admin)
    def delete(self, offer_id):
        """Supprime une offre."""
        offer = Offer.query.get_or_404(offer_id)
        db.session.delete(offer)
        db.session.commit()
        return {"message": "Offre supprimée avec succès"}, 204

