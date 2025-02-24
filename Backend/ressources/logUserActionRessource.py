#from urllib import request
from flask import request
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from decorators import role_required
from models import db, LogUserAction
from schemas import LogUserActionSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
import jwt


log_user_action_ns = Namespace('user_actions', description='Tracking user actions and logs')


@log_user_action_ns.route('/<int:log_user_action_id>')
class LogUserActionResource(Resource):
    # Initialiser les schémas
    log_user_action_schema = LogUserActionSchema()
    log_user_action_list_schema = LogUserActionSchema(many=True)

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def get(self, log_user_action_id=None):
        """Récupère une action utilisateur spécifique ou toutes les actions, avec filtrage par user_id."""

        # Initialiser le parser pour les arguments
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, location='args', help="ID de l'utilisateur pour filtrer les logs")
        args = parser.parse_args()

        # Récupérer la valeur de user_id
        user_id = args.get('user_id')

        # Vérifier si un ID spécifique d'action est demandé
        if log_user_action_id:
            log_user_action = LogUserAction.query.get_or_404(log_user_action_id, description="Log not found")
            return self.log_user_action_schema.dump(log_user_action), 200

        # Construire une requête avec un filtrage optionnel par user_id
        query = LogUserAction.query
        if user_id:
            query = query.filter_by(user_id=user_id)

        # Récupérer les résultats filtrés
        filtered_logs = query.all()

        if not filtered_logs:
            return {"message": "No logs found for the given criteria"}, 404

        return self.log_user_action_list_schema.dump(filtered_logs), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def post(self):
        """Crée une nouvelle action utilisateur."""
        try:
            new_log_user_action_data = self.log_user_action_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        new_log_user_action = LogUserAction(**new_log_user_action_data)
        db.session.add(new_log_user_action)
        db.session.commit()
        return self.log_user_action_schema.dump(new_log_user_action), 201

    @jwt_required()
    @role_required(7)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def put(self, log_user_action_id):
        """Remplace complètement une action utilisateur existante."""
        log_user_action = LogUserAction.query.get_or_404(log_user_action_id)

        try:
            updated_log_user_action_data = self.log_user_action_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_log_user_action_data.items():
            setattr(log_user_action, key, value)

        db.session.commit()
        return self.log_user_action_schema.dump(log_user_action), 200

    @jwt_required()
    @role_required(7)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def delete(self, log_user_action_id):
        """Supprime une action utilisateur."""
        log_user_action = LogUserAction.query.get_or_404(log_user_action_id)
        db.session.delete(log_user_action)
        db.session.commit()
        return {"message": "Action utilisateur supprimée avec succès"}, 204

