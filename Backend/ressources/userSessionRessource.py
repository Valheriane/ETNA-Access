from flask import request
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from models import db, UserSession
from schemas import UserSessionSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from decorators import role_required  # Décorateur pour gérer les permissions

user_session_ns = Namespace('user_sessions', description='Gestion des sessions utilisateur')


@user_session_ns.route('/')
class UserSessionListResource(Resource):
    user_session_list_schema = UserSessionSchema(many=True)

    @jwt_required()
    @role_required(1)  # Tous les utilisateurs authentifiés peuvent voir leurs propres sessions
    def get(self):
        """ Récupère toutes les sessions de l'utilisateur ou toutes si admin """

        claims = get_jwt_identity()
        current_user = claims.get("id_user")
        current_user_permission = claims.get("permissions")

        # Ajout du support des filtres
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, location='args', help="ID de l'utilisateur pour filtrer")
        parser.add_argument('is_active', type=str, location='args', help="Filtrer par statut actif/inactif")
        args = parser.parse_args()

        is_active = args.is_active
        if is_active is not None:
            is_active = is_active == '1'

        # Un utilisateur non admin ne peut voir que ses propres sessions
        if args.user_id:
            if current_user_permission < 5 and args.user_id != current_user:
                return {"message": "Accès interdit : vous ne pouvez voir que vos propres sessions."}, 403
            query = UserSession.query.filter_by(user_id=args.user_id)
        else:
            if current_user_permission >= 5:  # Admin (5+)
                query = UserSession.query
            else:
                query = UserSession.query.filter_by(user_id=current_user)

        # Appliquer le filtre `is_active`
        if is_active is not None:
            query = query.filter_by(is_active=is_active)

        sessions = query.all()

        return self.user_session_list_schema.dump(sessions), 200

    @jwt_required()
    @role_required(1)  # Tous les utilisateurs peuvent créer leur propre session
    def post(self):
        """Créer une nouvelle session utilisateur"""

        claims = get_jwt_identity()
        current_user = claims.get("id_user")  # Récupération automatique du user_id

        try:
            # Charger les données de la requête SANS le user_id (on l'ajoutera nous-mêmes)
            new_session_data = UserSessionSchema(exclude=["user_id"]).load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        # Forcer le user_id avec celui du token JWT
        new_session_data["user_id"] = current_user

        new_session = UserSession(**new_session_data)
        db.session.add(new_session)
        db.session.commit()

        return UserSessionSchema().dump(new_session), 201



@user_session_ns.route('/<int:user_session_id>')
class UserSessionResource(Resource):
    user_session_schema = UserSessionSchema()

    @jwt_required()
    @role_required(1)  # Tous les utilisateurs authentifiés peuvent voir leurs propres sessions
    def get(self, user_session_id):
        """Récupérer une session utilisateur spécifique"""
        
        claims = get_jwt_identity()
        current_user = claims.get("id_user")
        current_user_permission = claims.get("permissions")
        user_session = UserSession.query.get_or_404(user_session_id)

        # Vérification des droits d'accès
        if user_session.user_id != current_user and current_user_permission < 5:
            return {"message": "Accès interdit à cette session."}, 403

        return self.user_session_schema.dump(user_session), 200

    @jwt_required()
    @role_required(1)  # Un utilisateur ne peut modifier que sa propre session
    def put(self, user_session_id):
        """Met à jour une session utilisateur existante"""

        claims = get_jwt_identity()
        current_user = claims.get("id_user")
        current_user_permission = claims.get("permissions")
        user_session = UserSession.query.get_or_404(user_session_id)

        # Vérification des droits d'accès
        if user_session.user_id != current_user and current_user_permission < 5:
            return {"message": "Vous ne pouvez modifier que vos propres sessions."}, 403

        try:
            updated_data = UserSessionSchema().load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_data.items():
            setattr(user_session, key, value)

        db.session.commit()
        return self.user_session_schema.dump(user_session), 200

    @jwt_required()
    @role_required(1)  # Un utilisateur ne peut supprimer que sa propre session
    def delete(self, user_session_id):
        """Supprimer une session utilisateur"""

        claims = get_jwt_identity()
        current_user = claims.get("id_user")
        current_user_permission = claims.get("permissions")
        user_session = UserSession.query.get_or_404(user_session_id)

        # Seul le propriétaire ou un admin peut supprimer la session
        if user_session.user_id != current_user and current_user_permission < 5:
            return {"message": "Vous ne pouvez supprimer que vos propres sessions."}, 403

        db.session.delete(user_session)
        db.session.commit()
        return {"message": "Session supprimée avec succès"}, 204
