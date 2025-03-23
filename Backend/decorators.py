from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask import request


from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def role_required(required_permission):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            print("Inside decorator")  # Debugging
            verify_jwt_in_request()  # Vérifie que le JWT est valide
            claims = get_jwt_identity()  # Récupère l'identité à partir du token
            print(f"Claims: {claims}")  # Debugging
            
            # Récupération des permissions de l'utilisateur
            user_permissions = claims.get('permissions', [])
            
            if not user_permissions:  # Vérifie que l'utilisateur a des permissions
                print("Permissions not in claims")  # Debugging
                response = jsonify({"message": "Permission denied"})
                response.status_code = 403
                return response
            
            # Vérifie si l'utilisateur a la permission requise
            if user_permissions < required_permission:
                print(f"User permissions: {user_permissions}, Required: {required_permission}")  # Debugging
                response = jsonify({"message": "Permission denied"})
                response.status_code = 403
                return response
            
            # Si tout est valide, on exécute la fonction originale
            return fn(*args, **kwargs)
        return decorator
    return wrapper



def requires_auth(permission=None):  # Optionnellement, vérifie une permission spécifique
    def decorator(f):  # Enveloppe la fonction cible
        @wraps(f)  # Conserve les métadonnées de la fonction originale
        def wrapper(*args, **kwargs):
            # Récupère le token depuis les en-têtes HTTP
            token = request.headers.get('Authorization')
            if not token:  # Si le token est absent, refuse l'accès
                return {"message": "Unauthorized"}, 401
            
            # Si une permission spécifique est définie, vérifie-la
            if permission and not has_permission(token, permission):
                return {"message": "Forbidden"}, 403
            
            # Si toutes les vérifications passent, exécute la fonction originale
            return f(*args, **kwargs)
        return wrapper
    return decorator

