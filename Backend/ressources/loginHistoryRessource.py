#from urllib import request
from flask import request
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from decorators import role_required
from models import db,LoginHistory
from schemas import LoginHistorySchema
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
import jwt


login_history_ns = Namespace('login_history', description='User login history tracking')


@login_history_ns.route('/<int:login_history_id>')
class LoginHistoryResource(Resource):
    # Initialiser les schémas
    login_history_schema = LoginHistorySchema()
    login_history_list_schema = LoginHistorySchema(many=True)

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def get(self, login_history_id=None):
        """Récupère un historique de connexion spécifique ou tous les historiques, avec un filtrage optionnel par user_id."""

        # Initialiser le parser pour les arguments
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, location='args', help="ID de l'utilisateur pour filtrer l'historique")
        args = parser.parse_args()

        # Récupérer la valeur de user_id
        user_id = args.get('user_id')

        # Vérifier si un ID spécifique d'historique de connexion est demandé
        if login_history_id:
            login_history = LoginHistory.query.get_or_404(login_history_id)
            return self.login_history_schema.dump(login_history), 200

        # Construire une requête avec un filtrage optionnel par user_id
        query = LoginHistory.query
        if user_id:
            query = query.filter_by(user_id=user_id)

        # Récupérer tous les résultats filtrés
        filtered_login_history = query.all()

        if not filtered_login_history:
            return {"message": "No login history found for the given user"}, 404

        # Retourner les données filtrées
        return self.login_history_list_schema.dump(filtered_login_history), 200

    @jwt_required()
    @role_required(5)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def post(self):
        """Crée une nouvelle entrée d'historique de connexion."""
        try:
            new_login_history_data = self.login_history_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        new_login_history = LoginHistory(**new_login_history_data)
        db.session.add(new_login_history)
        db.session.commit()
        return self.login_history_schema.dump(new_login_history), 201

    @jwt_required()
    @role_required(7)  # Exemple : accès pour les utilisateurs avec un rôle >= 4 (Admin)
    def delete(self, login_history_id):
        """Supprime un historique de connexion."""
        login_history = LoginHistory.query.get_or_404(login_history_id)
        db.session.delete(login_history)
        db.session.commit()
        return {"message": "Historique de connexion supprimé avec succès"}, 204
    
    