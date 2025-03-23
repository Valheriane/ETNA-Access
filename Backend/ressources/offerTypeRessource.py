#from urllib import request
from flask import request
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from decorators import role_required
from models import db, OfferTypes
from schemas import OfferTypeSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
import jwt


offer_type_ns = Namespace('offer_types', description='Types of offers available')


@offer_type_ns.route('/<int:offer_type_id>')
class OfferTypeResource(Resource):
    # Initialiser les schémas
    offer_type_schema = OfferTypeSchema()
    offer_type_list_schema = OfferTypeSchema(many=True)
    offer_type_patch_schema = OfferTypeSchema(partial=True)

    #@jwt_required()
    #@role_required(2)  # Exemple : accès pour les utilisateurs avec un rôle >= 2
    def get(self, offer_type_id=None):
        """Récupère un type d'offre spécifique ou tous les types d'offres."""
        if offer_type_id:
            offer_type = OfferTypes.query.get_or_404(offer_type_id)
            return self.offer_type_schema.dump(offer_type), 200

        all_offer_types = OfferTypes.query.all()
        return self.offer_type_list_schema.dump(all_offer_types), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def post(self):
        """Crée un nouveau type d'offre."""
        try:
            new_offer_type_data = self.offer_type_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        new_offer_type = OfferTypes(**new_offer_type_data)
        db.session.add(new_offer_type)
        db.session.commit()
        return self.offer_type_schema.dump(new_offer_type), 201

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def put(self, offer_type_id):
        """Remplace complètement un type d'offre existant."""
        offer_type = OfferTypes.query.get_or_404(offer_type_id)

        try:
            updated_offer_type_data = self.offer_type_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_offer_type_data.items():
            setattr(offer_type, key, value)

        db.session.commit()
        return self.offer_type_schema.dump(offer_type), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def patch(self, offer_type_id):
        """Met à jour partiellement un type d'offre."""
        offer_type = OfferTypes.query.get_or_404(offer_type_id)

        try:
            updated_offer_type_data = self.offer_type_patch_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_offer_type_data.items():
            if value is not None:
                setattr(offer_type, key, value)

        db.session.commit()
        return self.offer_type_schema.dump(offer_type), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 4 (Admin)
    def delete(self, offer_type_id):
        """Supprime un type d'offre."""
        offer_type = OfferTypes.query.get_or_404(offer_type_id)
        db.session.delete(offer_type)
        db.session.commit()
        return {"message": "Type d'offre supprimé avec succès"}, 204
    
    
    