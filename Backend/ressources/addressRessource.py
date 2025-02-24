#from urllib import request
from flask import request
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from models import FonctionCompany, db, Address, Users   
from schemas import AddressSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
import jwt
from flask_restful import abort
from app import check_permissions
from decorators import role_required
from marshmallow import ValidationError


address_ns = Namespace('addresses', description='Address management for users and companies')


@address_ns.route('/<int:address_id>')
class AddressResource(Resource):

    # Initialiser les schémas
    address_schema = AddressSchema()
    address_list_schema = AddressSchema(many=True)
    address_patch_schema = AddressSchema(partial=True)

    @jwt_required()
    @role_required(1)
    def get(self, address_id=None):
        """
        Récupère une adresse spécifique ou toutes les adresses avec des filtres optionnels.
        Vérifie les permissions utilisateur avant de retourner les données.
        """
        # Récupération des informations d'identité du JWT
        claims = get_jwt_identity()
        user_id_from_token = claims.get("id_user")
        user_permission = claims.get("permissions")
        company_id_from_token = claims.get("company_id")

        if address_id:
            address = Address.query.get_or_404(address_id, description="Adresse non trouvée.")
            
            # Vérification des droits d'accès
            if not check_permissions(
                user_permission=user_permission,
                target_user_id=address.user_id,
                user_id_from_token=user_id_from_token,
                company_id_from_token=company_id_from_token,
                target_company_id=address.company_id,
            ):
                return {"message": "Accès interdit."}, 403

            return self.address_schema.dump(address), 200

        # Récupération des paramètres de filtre
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, location='args')
        parser.add_argument('company_id', type=int, location='args')
        parser.add_argument('is_billing', type=bool, location='args')
        parser.add_argument('city', type=str, location='args')
        parser.add_argument('country', type=str, location='args')
        args = parser.parse_args()

        # Définition des filtres selon les permissions
        query = Address.query

        if user_permission in [1, 2]:
            query = query.filter_by(user_id=user_id_from_token)
        elif user_permission in [3, 4]:
            query = query.filter(Address.company_id == company_id_from_token)
        elif user_permission == 5:
            query = query.filter(Address.company_id != 1)  # Accès à toutes sauf admin principal
        elif user_permission == 6:
            query = query.filter((Address.company_id == company_id_from_token) | (Address.company_id != company_id_from_token))
        # Permission >= 7 : accès total, pas de filtre

        # Application des filtres optionnels
        if args['user_id'] is not None:
            query = query.filter_by(user_id=args['user_id'])
        if args['company_id'] is not None:
            query = query.filter_by(company_id=args['company_id'])
        if args['is_billing'] is not None:
            query = query.filter_by(is_billing=args['is_billing'])
        if args['city']:
            query = query.filter_by(city=args['city'])
        if args['country']:
            query = query.filter_by(country=args['country'])

        filtered_addresses = query.all()

        if not filtered_addresses:
            return {"message": "Aucune adresse correspondante ou autorisée."}, 404

        return self.address_list_schema.dump(filtered_addresses), 200

    @jwt_required()
    @role_required(1)  # Accès pour les utilisateurs avec un rôle >= 1
    def post(self):
        """Crée une nouvelle adresse avec des règles adaptées au rôle de l'utilisateur."""
        # Récupération des informations du JWT
        claims = get_jwt_identity()
        user_id_from_token = claims.get("id_user")
        user_role = claims.get("permissions")  # Vérifie bien que c'est le champ correct
        company_id_from_token = claims.get("company_id")

        try:
            # Charger les données envoyées par l'utilisateur
            new_address_data = self.address_schema.load(request.get_json())
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        # 🔹 Gestion des rôles :
        if user_role in [1, 2]:
            # Rang 1 & 2 : Adresse personnelle uniquement, pas d'association à l'entreprise
            new_address_data["user_id"] = user_id_from_token
            new_address_data["company_id"] = None

        elif user_role in [3, 4]: 
            # Récupérer l'ID de l'utilisateur cible (par défaut, c'est l'utilisateur qui fait la requête)
            target_user_id = new_address_data.get("user_id", user_id_from_token)  

            if target_user_id != user_id_from_token:
                # Vérifier que l'utilisateur cible appartient bien à la même entreprise
                target_user = (
                    db.session.query(FonctionCompany)
                    .filter(
                        FonctionCompany.user_id == target_user_id,
                        FonctionCompany.company_id == company_id_from_token
                    )
                    .first()
                )

                if not target_user:
                    return {"message": "L'utilisateur sélectionné n'appartient pas à votre entreprise."}, 403

                # Récupérer le rôle de l'utilisateur cible
                target_user_role = target_user.permission_id  # Assurez-vous que `role` est bien un champ dans le modèle User

                if user_role == 3 and target_user_role >= 4:
                    return {"message": "Vous ne pouvez pas ajouter une adresse pour un utilisateur de rang 4 ou supérieur."}, 403

            new_address_data["user_id"] = target_user_id  # Assigner l'adresse à l'utilisateur validé

            # Vérifier et attribuer la company_id
            if "company_id" not in new_address_data or new_address_data["company_id"] is None:
                new_address_data["company_id"] = None  # Permettre une adresse personnelle
            else:
                new_address_data["company_id"] = company_id_from_token  # Associer à l'entreprise



        elif user_role >= 5:
            # Rang 5+ : Peuvent créer des adresses pour d'autres utilisateurs sans restriction
            if "user_id" not in new_address_data or new_address_data["user_id"] is None:
                return {"message": "Vous devez spécifier un user_id."}, 400
            
            # Permettre de définir `company_id` librement
            if "company_id" not in new_address_data:
                new_address_data["company_id"] = None  # Autoriser une adresse sans entreprise

        else:
            return {"message": "Accès interdit."}, 403  # Protection en cas de rôle non prévu

        # 🔹 Création et sauvegarde de l'adresse
        new_address = Address(**new_address_data)
        db.session.add(new_address)
        db.session.commit()

        return self.address_schema.dump(new_address), 201



    @jwt_required()
    @role_required(1)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def put(self, address_id):
        """Modifie une adresse existante avec des règles de permission strictes."""

        # Récupération des informations du token
        claims = get_jwt_identity()
        user_id_from_token = claims.get("id_user")
        user_permission = claims.get("permissions")
        company_id_from_token = claims.get("company_id")

        # Récupération de l'adresse cible
        address = Address.query.get_or_404(address_id)

        # Vérification que l'utilisateur est lié à une entreprise et récupération de ses infos
        user_company = (
            db.session.query(FonctionCompany)
            .filter(FonctionCompany.user_id == user_id_from_token)
            .first()
        )

        if not user_company:
            return {"error": "Utilisateur non trouvé ou non associé à une entreprise."}, 404

        # Récupération des informations de l'utilisateur cible
        target_user_company = (
            db.session.query(FonctionCompany)
            .filter(FonctionCompany.user_id == address.user_id)
            .first()
        )

        if not target_user_company:
            return {"error": "Utilisateur cible non trouvé."}, 404

        # Vérification des permissions
        if not check_permissions(
            user_company.permission_id,
            target_user_id=address.user_id,
            user_id_from_token=user_id_from_token,
            company_id_from_token=user_company.company_id,
            target_company_id=target_user_company.company_id,
            target_user_permission=target_user_company.permission_id,
        ):
            return {"error": "Accès refusé : vous n'avez pas les droits pour modifier cette adresse."}, 403
        
        data = request.json.copy()
        data.pop("updated_at", None)
        data.pop("updated_at", None)# Supprime updated_at si présent dans la requête

        try:
            updated_address_data = self.address_schema.load(data)
        except ValidationError as err:
            return {"message": "Erreur de validation", "errors": err.messages}, 400


        for key, value in updated_address_data.items():
            setattr(address, key, value)

        db.session.commit()
        return self.address_schema.dump(address), 200


    @jwt_required()
    @role_required(1)  # Exemple : accès pour les utilisateurs avec un rôle >= 3 (Admin ou Manager)
    def patch(self, address_id):
        """Modifie une adresse existante avec des règles de permission strictes."""

        # Récupération des informations du token
        claims = get_jwt_identity()
        user_id_from_token = claims.get("id_user")
        user_permission = claims.get("permissions")
        company_id_from_token = claims.get("company_id")

        # Récupération de l'adresse cible
        address = Address.query.get_or_404(address_id)

        # Vérification que l'utilisateur est lié à une entreprise et récupération de ses infos
        user_company = (
            db.session.query(FonctionCompany)
            .filter(FonctionCompany.user_id == user_id_from_token)
            .first()
        )

        if not user_company:
            return {"error": "Utilisateur non trouvé ou non associé à une entreprise."}, 404

        # Récupération des informations de l'utilisateur cible
        target_user_company = (
            db.session.query(FonctionCompany)
            .filter(FonctionCompany.user_id == address.user_id)
            .first()
        )

        if not target_user_company:
            return {"error": "Utilisateur cible non trouvé."}, 404

        # Vérification des permissions
        if not check_permissions(
            user_company.permission_id,
            target_user_id=address.user_id,
            user_id_from_token=user_id_from_token,
            company_id_from_token=user_company.company_id,
            target_company_id=target_user_company.company_id,
            target_user_permission=target_user_company.permission_id,
        ):
            return {"error": "Accès refusé : vous n'avez pas les droits pour modifier cette adresse."}, 403
        
        data = request.json.copy()
        data.pop("updated_at", None)
        data.pop("updated_at", None)# Supprime updated_at si présent dans la requête

        try:
            updated_address_data = self.address_patch_schema.load(data)
        except ValidationError as err:
            return {"message": "Erreur de validation", "errors": err.messages}, 400


        for key, value in updated_address_data.items():
            setattr(address, key, value)

        db.session.commit()
        return self.address_schema.dump(address), 200


    @jwt_required()
    @role_required(1)  # Accès pour les utilisateurs avec un rôle >= 1
    def delete(self, address_id):
        """Supprime une adresse en respectant les règles de permissions."""

        # Récupération des informations du token
        claims = get_jwt_identity()
        user_id_from_token = claims.get("id_user")

        # Récupération de l'adresse cible
        address = Address.query.get_or_404(address_id)

        # Vérification que l'utilisateur est bien lié à une entreprise
        user_company = (
            db.session.query(FonctionCompany)
            .filter(FonctionCompany.user_id == user_id_from_token)
            .first()
        )

        if not user_company:
            return {"error": "Utilisateur non trouvé ou non associé à une entreprise."}, 404

        # Récupération des informations de l'utilisateur propriétaire de l'adresse
        target_user_company = (
            db.session.query(FonctionCompany)
            .filter(FonctionCompany.user_id == address.user_id)
            .first()
        )

        if not target_user_company:
            return {"error": "Utilisateur cible non trouvé."}, 404

        # Vérification des permissions AVANT de regarder le nombre d'adresses restantes
        if not check_permissions(
            user_company.permission_id,
            target_user_id=address.user_id,
            user_id_from_token=user_id_from_token,
            company_id_from_token=user_company.company_id,
            target_company_id=target_user_company.company_id,
            target_user_permission=target_user_company.permission_id,
        ):
            return {"message": "Vous n'avez pas l'autorisation de supprimer cette adresse."}, 403

        # Vérification du nombre d'adresses restantes pour l'utilisateur cible
        user_addresses_count = Address.query.filter_by(user_id=address.user_id).count()
        if user_addresses_count <= 1:
            return {"message": "L'utilisateur doit posséder au moins une adresse."}, 403

        # Suppression de l'adresse
        db.session.delete(address)
        db.session.commit()

        return {"message": "Adresse supprimée avec succès."}, 204







