from flask import session
from models import Users, PermissionSSO # Tes modèles de données
from sqlalchemy.orm import sessionmaker

def create_user_with_permissions(data):
    # Crée un nouvel utilisateur
    user = Users(username=data['username'], email=data['email'], password=data['password'])
    session.add(user)
    session.commit()

    # Récupère l'ID de l'utilisateur nouvellement créé
    user_id = user.id

    # Crée des permissions par défaut pour cet utilisateur
    permission = PermissionSSO(user_id=user_id, permission_level=1)
    session.add(permission)
    session.commit()

    # Si nécessaire, modifie la permission en fonction de la company_id
    if 'company_id' in data:
        permission.company_id = data['company_id']
        permission.permission_level = 2  # Par exemple, passage de 1 à 2
        session.commit()

    return user
