from flask_jwt_extended import get_jwt_identity

# Exemple de dictionnaire des permissions par rôle
PERMISSIONS = {
    1: ["read:profile"],
    2: ["read:profile", "write:profile"],
    3: ["read:profile", "write:profile", "manage:team"],
    4: ["*"],
    5: ["read:all_users", "write:logs"],
    6: ["manage:etna"],
    7: ["*"],
}

def has_permission(token, permission):
    """
    Vérifie si l'utilisateur a la permission demandée.
    
    :param token: Le token JWT de l'utilisateur.
    :param permission: La permission demandée.
    :return: True si l'utilisateur a la permission, False sinon.
    """
    # Récupère l'identité de l'utilisateur à partir du JWT
    claims = get_jwt_identity()  # Assure-toi que JWT est déjà vérifié avant d'appeler cette fonction
    
    if not claims or 'rang' not in claims:
        return False  # Aucun rang trouvé dans les claims, refus d'accès
    
    user_rang = claims['rang']
    user_permissions = PERMISSIONS.get(user_rang, [])  # Récupère les permissions associées au rang

    # Vérifie si l'utilisateur a la permission demandée
    if "*" in user_permissions or permission in user_permissions:
        return True
    
    return False

