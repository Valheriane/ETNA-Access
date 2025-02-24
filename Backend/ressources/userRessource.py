#from urllib import request
from flask import request
from flask import abort
from flask_restx import Resource, reqparse, Namespace
from jsonschema import ValidationError
from sqlalchemy import or_
from app import check_permissions
from decorators import role_required
from models import FonctionCompany, db, Users
from schemas import UserSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import bcrypt
import jwt


# Création d'un namespace
user_ns = Namespace('users', description='Operations related to users')

@user_ns.route('/<int:user_id>')
class UserResource(Resource):
     
    # Initialiser les schémas
    user_schema = UserSchema()
    user_list_schema = UserSchema(many=True)
    user_patch_schema = UserSchema(partial=True)

    @jwt_required()
    @role_required(1)
    def get(self, user_id=None):
        """
        Récupère un utilisateur spécifique ou tous les utilisateurs avec un filtre basé sur les permissions.

        :param user_id: Identifiant de l'utilisateur (facultatif).
        :return: Les données de l'utilisateur ou des utilisateurs filtrés, avec un code HTTP approprié.
        """
        # Récupérer les informations d'identité du JWT
        claims = get_jwt_identity()
        user_id_from_token = claims.get("id_user")
        user_permission = claims.get("permissions")
        company_id_from_token = claims.get("company_id")
        #print(" je suis dans le get " )
        #print(" Mon token :  ", claims )
        
        
        # Si un utilisateur spécifique est demandé
        if user_id:
            claims = get_jwt_identity()
            if not claims:
                return {"message": "Aucun JWT identity trouvé."}, 401
            print("Claims reçus : ", claims)

            user = Users.query.get_or_404(user_id, description="Utilisateur non trouvé.")
            user_company = FonctionCompany.query.filter_by(user_id=user_id).first()    

            if not user_company:
                abort(404, description="Aucune fonction associée à cet utilisateur.")

            # Vérification des droits d'accès
            has_permission = check_permissions(
                user_permission=user_permission,
                target_user_id=user_id,
                user_id_from_token=user_id_from_token,
                company_id_from_token=company_id_from_token,
                target_company_id=user_company.company_id,
                target_user_permission=user_company.permission_id  # Ajout de target_user_permission
            )
            print("has permission : ", has_permission)
            print(" user_id_from_token : ", user_id_from_token  , " et target_user_id : ", user_id  )
            print("target_user_permission ", user_company.permission_id, " et user_permission : ", user_permission)
            if not has_permission:
                return {"message": "Accès interdit."}, 403

            return self.user_schema.dump(user), 200

        # Sinon, récupérer tous les utilisateurs avec un filtre
        query = Users.query
        print("query: ", query)
        if user_permission in [1, 2]:
            query = query.filter_by(id_user=user_id_from_token)
        elif user_permission == 3:
            # Récupérer les utilisateurs des autres entreprises ou sans entreprise
            print(" je suis dans user permision = 3 " )

            # Récupérer les utilisateurs de l'entreprise actuelle (company_id = company_id_from_token)
            own_company_query = Users.query.join(FonctionCompany).filter(
                FonctionCompany.company_id == company_id_from_token,  # Limité à l'entreprise actuelle
                (FonctionCompany.permission_id <=2) | (Users.id_user == user_id_from_token)  # Permissions <= 5 ou soi-même
            )
            print("FonctionCompany.permission_id : ", FonctionCompany.permission_id, " Users.id_user : ", Users.id_user, " user_id_from_token : ", user_id_from_token  )
            # Inclure l'utilisateur lui-même explicitement
            #self_user_query = Users.query.filter(Users.id_user == user_id_from_token)
            # Combiner les deux requêtes
            query = own_company_query
            print("own_company_query : ", own_company_query)
        elif user_permission == 4:
            query = query.join(FonctionCompany).filter(FonctionCompany.company_id == company_id_from_token)
        elif user_permission == 5:
            print(" je suis dans user permision = 5 " )
            query = query.join(FonctionCompany).filter(FonctionCompany.company_id != 1)
        elif user_permission == 6:
            # Récupérer les utilisateurs des autres entreprises ou sans entreprise
            print(" je suis dans user permision = 6 " )
            other_companies_query = Users.query.outerjoin(FonctionCompany).filter(
                (FonctionCompany.company_id != company_id_from_token) | (FonctionCompany.company_id == None),  # Exclure company_id de l'utilisateur
                FonctionCompany.permission_id < 7  # Exclure les utilisateurs avec permission >= 7
            )
            # Récupérer les utilisateurs de l'entreprise actuelle (company_id = company_id_from_token)
            own_company_query = Users.query.join(FonctionCompany).filter(
                FonctionCompany.company_id == company_id_from_token,  # Limité à l'entreprise actuelle
                (FonctionCompany.permission_id <=5) | (Users.id_user == user_id_from_token)  # Permissions <= 5 ou soi-même
            )
            print("FonctionCompany.permission_id : ", FonctionCompany.permission_id, " Users.id_user : ", Users.id_user, " user_id_from_token : ", user_id_from_token  )
            # Inclure l'utilisateur lui-même explicitement
            #self_user_query = Users.query.filter(Users.id_user == user_id_from_token)
            # Combiner les deux requêtes
            query = other_companies_query.union(own_company_query)#, self_user_query
            print("own_company_query : ", own_company_query)

        elif user_permission >= 7:
            print(" je suis dans user permision >= 7 " )
            # Pas de filtre : accès à tout
            pass
        else:
            # Permissions non gérées
            return {"message": "Permissions insuffisantes."}, 403

        # Récupérer les résultats filtrés
        filtered_users = query.all()

        if not filtered_users:
            return {"message": "Aucun utilisateur ne correspond aux critères donnés."}, 404

        return self.user_list_schema.dump(filtered_users), 200

    #@jwt_required()
    #@role_required()  # Exemple : accès pour les utilisateurs avec un rôle >= 3
    #@requires_auth(permission="read:protected")
    def post(self):
        """Crée un nouvel utilisateur."""
        try:
            # Charger et valider les données du JSON
            new_user_data = self.user_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        # Hashage du mot de passe
        hashed_password = bcrypt.generate_password_hash(new_user_data['password']).decode('utf-8')
        new_user_data['password'] = hashed_password

        # Créer un nouvel utilisateur
        new_user = Users(**new_user_data)

        db.session.add(new_user)
        db.session.commit()

        return self.user_schema.dump(new_user), 201


    @jwt_required()
    @role_required(1)  # Exemple : accès pour les utilisateurs avec un rôle >= 1
    def put(self, user_id):
        """Met à jour un utilisateur existant en fonction des permissions."""
        # Récupère l'utilisateur à modifier
        user = Users.query.get_or_404(user_id)

        # Récupérer les informations d'identité du JWT
        claims = get_jwt_identity()
        user_id_from_token = claims.get("id_user")
        user_permission = claims.get("permissions")
        company_id_from_token = claims.get("company_id")

        # Récupère l'instance de FonctionCompany pour l'utilisateur spécifié
        user_target = FonctionCompany.query.filter_by(user_id=user_id).first()

       

        # Vérifie si l'utilisateur a la permission de modifier cet utilisateur
        if not check_permissions(
            user_permission=user_permission,
            target_user_id=user_id,
            user_id_from_token=user_id_from_token,
            company_id_from_token=company_id_from_token,
            target_company_id=user_target.company_id,
            target_user_permission=user_target.permission_id
        ):  
            return {"message": "Access denied: You do not have permission to modify this user."}, 403
        
        data = request.json.copy()
        data.pop("updated_at", None)
        data.pop("updated_at", None)
        try:
            # Charge les données envoyées dans la requête
            updated_user_data = self.user_schema.load(request.json)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400
        
        # Hashage du mot de passe si nécessaire
        if 'password' in updated_user_data:
            updated_user_data['password'] = bcrypt.generate_password_hash(updated_user_data['password']).decode('utf-8')

        # Applique les modifications sur l'utilisateur
        for key, value in updated_user_data.items():
            setattr(user, key, value)

        # Enregistre les modifications dans la base de données
        db.session.commit()

        # Retourne les données mises à jour
        return self.user_schema.dump(user), 200


    @jwt_required()
    @role_required(1)  # Exemple : accès pour les utilisateurs avec un rôle >= 1
    def patch(self, user_id):
        """Met à jour partiellement un utilisateur."""
        # Récupère l'utilisateur à modifier
        user = Users.query.get_or_404(user_id)

        # Récupérer les informations d'identité du JWT
        claims = get_jwt_identity()
        user_id_from_token = claims.get("id_user")
        user_permission = claims.get("permissions")
        company_id_from_token = claims.get("company_id")

        # Récupère l'instance de FonctionCompany pour l'utilisateur spécifié
        user_target = FonctionCompany.query.filter_by(user_id=user_id).first()

        # Vérifie si l'utilisateur a la permission de modifier cet utilisateur
        if not check_permissions(
            user_permission=user_permission,
            target_user_id=user_id,
            user_id_from_token=user_id_from_token,
            company_id_from_token=company_id_from_token,
            target_company_id=user_target.company_id,
            target_user_permission=user_target.permission_id
        ):  
            return {"message": "Access denied: You do not have permission to modify this user."}, 403

        try:
            # Charge les données envoyées dans la requête pour validation partielle
            updated_user_data = self.user_patch_schema.load(request.json, partial=True)
        except ValidationError as err:
            return {"message": "Validation error", "errors": err.messages}, 400

        # Hashage du mot de passe si fourni
        if 'password' in updated_user_data:
            updated_user_data['password'] = bcrypt.generate_password_hash(updated_user_data['password']).decode('utf-8')

        # Applique les modifications sur l'utilisateur
        for key, value in updated_user_data.items():
            if value is not None:
                setattr(user, key, value)

        # Enregistre les modifications dans la base de données
        db.session.commit()

        # Retourne les données mises à jour
        return self.user_schema.dump(user), 200


    @jwt_required()
    @role_required(4)  # Exemple : accès pour les utilisateurs avec un rôle >= 4
    def delete(self, user_id):
        """Supprime un utilisateur après vérification des permissions."""
        # Récupère l'utilisateur à supprimer
        user = Users.query.get_or_404(user_id)

        # Récupérer les informations d'identité du JWT
        claims = get_jwt_identity()
        user_id_from_token = claims.get("id_user")
        user_permission = claims.get("permissions")
        company_id_from_token = claims.get("company_id")

        # Récupère l'instance de FonctionCompany pour l'utilisateur spécifié
        user_target = FonctionCompany.query.filter_by(user_id=user_id).first()

        # Vérifie si l'utilisateur a la permission de supprimer cet utilisateur
        if not check_permissions(
            user_permission=user_permission,
            target_user_id=user_id,
            user_id_from_token=user_id_from_token,
            company_id_from_token=company_id_from_token,
            target_company_id=user_target.company_id,
            target_user_permission=user_target.permission_id
        ):
            return {
                "message": "Access denied: You do not have permission to delete this user. Please contact your administrator."
            }, 403
        if user_id_from_token == user_id:
            return {
                "message": "You cannot delete your own account. Please contact your administrator."
            }, 403
        # Vérifie si l'utilisateur connecté a le rôle suffisant permisison = ou > à 4, pour supprimer
        if user_permission < 3:
            return {
                "message": "Only users with a role of 4 or higher can delete other users. Please contact your administrator."
            }, 403

        # Supprime l'utilisateur
        db.session.delete(user)
        db.session.commit()

        return {"message": "Utilisateur supprimé avec succès"}, 204



