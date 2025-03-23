#from urllib import request
from flask import request
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from models import db, PaymentMethod
from schemas import PaymentMethodSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
import jwt


payment_ns = Namespace('payments', description='Payment operations and processing')


@payment_ns.route('/<int:payment_method_id>')
class PaymentMethodResource(Resource):
     
    # Initialiser les schémas
    payment_method_schema = PaymentMethodSchema()
    payment_method_list_schema = PaymentMethodSchema(many=True)
    payment_method_patch_schema = PaymentMethodSchema(partial=True)

    @jwt_required()
    #@role_required(2)  # Exemple : accès pour les utilisateurs avec un rôle >= 2
    def get(self, payment_method_id=None):
        """Récupère un moyen de paiement spécifique ou applique des filtres."""
        # Initialiser le parser pour les arguments
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, location='args', help="Filtre par ID d'utilisateur")
        parser.add_argument('company_id', type=int, location='args', help="Filtre par ID d'entreprise")
        parser.add_argument('is_active', type=bool, location='args', help="Filtre par statut actif/inactif")
        args = parser.parse_args()

        # Récupérer les valeurs des arguments
        user_id = args.get('user_id')
        company_id = args.get('company_id')
        is_active = args.get('is_active')

        # Si un ID spécifique est fourni, récupérer ce moyen de paiement
        if payment_method_id:
            payment_method = PaymentMethod.query.get_or_404(payment_method_id, description="Payment method not found")
            return self.payment_method_schema.dump(payment_method), 200

        # Construire la requête avec des filtres dynamiques
        query = PaymentMethod.query
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        if company_id is not None:
            query = query.filter_by(company_id=company_id)
        if is_active is not None:
            query = query.filter_by(is_active=is_active)

        # Exécuter la requête filtrée
        filtered_payment_methods = query.all()
        if not filtered_payment_methods:
            return {"message": "No payment methods match the given criteria"}, 404

        return self.payment_method_list_schema.dump(filtered_payment_methods), 200

    @jwt_required()
    #@role_required(2)  # Exemple : accès pour les utilisateurs avec un rôle >= 2
    def post(self):
        """Crée un nouveau moyen de paiement."""
        try:
            new_payment_method_data = self.payment_method_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        new_payment_method = PaymentMethod(**new_payment_method_data)
        db.session.add(new_payment_method)
        db.session.commit()
        return self.payment_method_schema.dump(new_payment_method), 201

    @jwt_required()
    #@role_required(3)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def put(self, payment_method_id):
        """Remplace complètement un moyen de paiement existant."""
        payment_method = PaymentMethod.query.get_or_404(payment_method_id)

        try:
            updated_payment_method_data = self.payment_method_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_payment_method_data.items():
            setattr(payment_method, key, value)

        db.session.commit()
        return self.payment_method_schema.dump(payment_method), 200

    @jwt_required()
    #@role_required(3)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def patch(self, payment_method_id):
        """Met à jour partiellement un moyen de paiement."""
        payment_method = PaymentMethod.query.get_or_404(payment_method_id)

        try:
            updated_payment_method_data = self.payment_method_patch_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        for key, value in updated_payment_method_data.items():
            if value is not None:
                setattr(payment_method, key, value)

        db.session.commit()
        return self.payment_method_schema.dump(payment_method), 200

    @jwt_required()
    #@role_required(4)  # Exemple : accès pour les utilisateurs avec un rôle >= 4 (Admin)
    def delete(self, payment_method_id):
        """Supprime un moyen de paiement."""
        payment_method = PaymentMethod.query.get_or_404(payment_method_id)
        db.session.delete(payment_method)
        db.session.commit()
        return {"message": "Moyen de paiement supprimé avec succès"}, 204
