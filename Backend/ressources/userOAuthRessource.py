from flask import request
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from models import db, UserOAuth
from schemas import UserOAuthSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from decorators import role_required  # Assure-toi que ce décorateur gère bien tes niveaux d'accès

user_oauth_ns = Namespace('user_oauth', description='OAuth integrations for users')

@user_oauth_ns.route('/')
class UserOAuthListResource(Resource):
    user_oauth_list_schema = UserOAuthSchema(many=True)

    @jwt_required()
    @role_required(1)  # Accessible à tous les utilisateurs authentifiés
    def get(self):
        """ Récupère toutes les connexions OAuth de l'utilisateur ou toutes si admin """
        
        claims = get_jwt_identity()
        current_user = claims.get("id_user")
        current_user_permission = claims.get("permissions")

        # Ajout du support des filtres
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, location='args', help="ID de l'utilisateur pour filtrer")
        parser.add_argument('provider_id', type=int, location='args', help="Filtrer par provider OAuth")
        parser.add_argument('is_active', type=str, location='args', help="Filtrer par statut actif/inactif")
        args = parser.parse_args()

        is_active = args.is_active
        if is_active is not None:
            is_active = is_active == '1'

        # Gestion des droits : Un utilisateur ne peut voir que ses propres connexions
        if args.user_id:
            if current_user_permission < 5 and args.user_id != current_user:
                return {"message": "Accès interdit : vous ne pouvez voir que vos propres connexions"}, 403
            query = UserOAuth.query.filter_by(user_id=args.user_id)
        else:
            if current_user_permission >= 5:  # Admin (5+)
                query = UserOAuth.query
            else:
                query = UserOAuth.query.filter_by(user_id=current_user.id)

        # Appliquer les autres filtres
        if args.provider_id:
            query = query.filter_by(provider_id=args.provider_id)
        if is_active is not None:
            query = query.filter_by(is_active=is_active)

        oauth_connections = query.all()

        return self.user_oauth_list_schema.dump(oauth_connections), 200

    @jwt_required()
    @role_required(1)  # Tous les utilisateurs peuvent ajouter une connexion OAuth pour eux-mêmes
    def post(self):
        """Associer un compte OAuth à l'utilisateur courant"""
        claims = get_jwt_identity()
        current_user = claims.get("id_user")
        current_user_permission = claims.get("permissions")
        
        try:
            new_oauth_data = UserOAuthSchema().load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        if new_oauth_data["user_id"] != current_user and current_user_permission < 5:
            return {"message": "Vous ne pouvez ajouter une connexion OAuth que pour vous-même."}, 403

        new_user_oauth = UserOAuth(**new_oauth_data)
        db.session.add(new_user_oauth)
        db.session.commit()

        return UserOAuthSchema().dump(new_user_oauth), 201


@user_oauth_ns.route('/<int:user_oauth_id>')
class UserOAuthResource(Resource):
    user_oauth_schema = UserOAuthSchema()

    @jwt_required()
    @role_required(1)  # Tous les utilisateurs authentifiés peuvent voir leurs propres connexions
    def get(self, user_oauth_id):
        """Récupérer une connexion OAuth spécifique"""
        claims = get_jwt_identity()
        current_user = claims.get("id_user")
        current_user_permission = claims.get("permissions")
        user_oauth = UserOAuth.query.get_or_404(user_oauth_id)

        # Vérification des droits d'accès
        if user_oauth.user_id != current_user and current_user_permission < 5:
            return {"message": "Accès interdit à cette ressource."}, 403

        return self.user_oauth_schema.dump(user_oauth), 200

    @jwt_required()
    @role_required(1)  # Tous les utilisateurs peuvent supprimer leurs propres connexions
    def delete(self, user_oauth_id):
        """Dissocier un compte OAuth"""
        claims = get_jwt_identity()
        current_user = claims.get("id_user")
        current_user_permission = claims.get("permissions")
        user_oauth = UserOAuth.query.get_or_404(user_oauth_id)

        # Seul le propriétaire ou un admin peut supprimer la connexion
        if user_oauth.user_id != current_user and current_user_permission < 5:
            return {"message": "Vous ne pouvez supprimer que vos propres connexions OAuth."}, 403

        db.session.delete(user_oauth)
        db.session.commit()
        return {"message": "Connexion OAuth supprimée avec succès"}, 204
