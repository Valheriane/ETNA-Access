#from urllib import request
from flask import request
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from decorators import role_required
from models import db, OAuthProvider
from schemas import OAuthProviderSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
import jwt

oauth_provider_ns = Namespace('oauth_providers', description='OAuth provider management (Google, Facebook, etc.)')


@oauth_provider_ns.route('/<int:provider_id>')
class OAuthProviderRessource(Resource):
    
    # Schéma pour OAuthProvider
    oauth_provider_schema = OAuthProviderSchema()  # Schéma pour un fournisseur OAuth unique
    oauth_provider_list_schema = OAuthProviderSchema(many=True)  # Schéma pour une liste de fournisseurs

    @jwt_required()
    @role_required(5) 
    def get(self, provider_id=None):
        """
        GET: Récupérer un fournisseur OAuth spécifique ou la liste complète.
        """
        if provider_id:
            provider = OAuthProvider.query.get(provider_id)
            if not provider:
                return {"message": "OAuth provider not found."}, 404
            return self.oauth_provider_schema.dump(provider), 200
        providers = OAuthProvider.query.all()
        return self.oauth_provider_list_schema.dump(providers), 200

    @jwt_required()
    @role_required(5) 
    def post(self):
        """
        POST: Créer un nouveau fournisseur OAuth.
        """
        try:
            data = request.get_json()
            provider = self.oauth_provider_schema.load(data)
            db.session.add(provider)
            db.session.commit()
            return self.oauth_provider_schema.dump(provider), 201
        except ValidationError as err:
            return {"errors": err.messages}, 400

    @jwt_required()
    @role_required(5) 
    def put(self, provider_id):
        """
        PUT: Mettre à jour un fournisseur OAuth existant.
        """
        provider = OAuthProvider.query.get(provider_id)
        if not provider:
            return {"message": "OAuth provider not found."}, 404
        try:
            data = request.get_json()
            provider = self.oauth_provider_schema.load(data, instance=provider, partial=True)
            db.session.commit()
            return self.oauth_provider_schema.dump(provider), 200
        except ValidationError as err:
            return {"errors": err.messages}, 400

    @jwt_required()
    @role_required(5) 
    def delete(self, provider_id):
        """
        DELETE: Supprimer un fournisseur OAuth.
        """
        provider = OAuthProvider.query.get(provider_id)
        if not provider:
            return {"message": "OAuth provider not found."}, 404
        db.session.delete(provider)
        db.session.commit()
        return {"message": "OAuth provider deleted successfully."}, 200


