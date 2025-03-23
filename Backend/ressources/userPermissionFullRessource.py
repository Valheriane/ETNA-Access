from flask_restful import Resource
from flask import request
from services.userService import create_user_with_permissions

class UserPermissionFullResource(Resource):
    def post(self):
        data = request.get_json()  # Récupère les données envoyées dans la requête
        try:
            # Appelle le service pour créer l'utilisateur et ses permissions
            user = create_user_with_permissions(data)
            return {"message": "User created successfully", "user": user.to_dict()}, 201
        except Exception as e:
            return {"message": str(e)}, 400
