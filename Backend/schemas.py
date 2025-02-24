import datetime
from datetime import datetime, date, timedelta
from flask_marshmallow import Marshmallow
from marshmallow import fields, post_load
from models import (
    FonctionCompany, Users, Company, Address, Images, Product, PermissionSSO,
    LicenseMode, TypeImgs, AccessRights, Offer, ProductImgs, 
    OfferProducts, ProductConfigurations, License, PaymentMethod,
    OfferTypes, LoginHistory, OAuthProvider, UserOAuth, UserSession, LogUserAction
)

ma = Marshmallow()

class BaseSchema(ma.SQLAlchemyAutoSchema):
    created_at = fields.DateTime(dump_only=True)  # ✅ Ne peut pas être modifié
    updated_at = fields.DateTime(dump_only=True)  # ✅ Géré par SQLAlchemy, pas modifiable

    @post_load
    def handle_dates(self, data, **kwargs):
        if "created_at" not in data:  # ✅ Vérifie avant de toucher à `created_at`
            data["created_at"] = datetime.now()
        data["updated_at"] = datetime.now()  # Toujours mettre à jour `updated_at`
        return data

        return data

# Exemple de schémas
class UserSchema(BaseSchema):
    class Meta:
        model = Users
        #load_instance = True
        include_relationships = False
        include_fk = True

    password = fields.String(load_only=True)  # Cacher le mot de passe lors de la sérialisation

class CompanySchema(BaseSchema):
    class Meta:
        model = Company
        #load_instance = True
        include_relationships = False
        include_fk = True

class AddressSchema(BaseSchema):
    class Meta:
        model = Address
        #load_instance = True
        include_relationships = False #Permets d'afficher les relation entre [] True , Pas de relation False
        include_fk = True

class ImageSchema(BaseSchema):
    class Meta:
        model = Images
        #load_instance = True
        include_fk = True

class ProductSchema(BaseSchema):
    #created_at = fields.DateTime(required=False,  dump_only=True)
    #updated_at = fields.DateTime(required=False, allow_none=True)
    class Meta:
        model = Product
        #load_instance = True
        include_relationships = False
        include_fk = True

class PermissionSSOSchema(BaseSchema):
    class Meta:
        model = PermissionSSO
        #load_instance = True

class LicenseModeSchema(BaseSchema):
    class Meta:
        model = LicenseMode
        #load_instance = True

class TypeImgsSchema(BaseSchema):
    class Meta:
        model = TypeImgs
        #load_instance = True

class AccessRightsSchema(BaseSchema):
    class Meta:
        model = AccessRights
        #load_instance = True

class OfferSchema(BaseSchema):
    #created_at = fields.DateTime(required=False,  dump_only=True)
    #updated_at = fields.DateTime(required=False, allow_none=True)
    class Meta:
        model = Offer
        #load_instance = True
        include_fk = True

class OfferProductSchema(BaseSchema):
    class Meta:
        model = OfferProducts
        #load_instance = True
        include_fk = True

class ProductImgsSchema(BaseSchema):
    class Meta:
        model = ProductImgs
        #load_instance = True
        include_fk = True

    product = fields.Nested(ProductSchema, only=["id_product", "name"])
    image = fields.Nested(ImageSchema, only=["id_image", "url"])


class ProductConfigurationSchema(BaseSchema):
    class Meta:
        model = ProductConfigurations
        #load_instance = True
        include_fk = True

    product = fields.Nested(ProductSchema, only=["id_product", "name", "type"])


class LicenseSchema(BaseSchema):
    class Meta:
        model = License
        #load_instance = True
        include_relationships = False
        include_fk = True

    product = fields.Nested(ProductSchema, only=["id_product", "name", "type"])
    user = fields.Nested("UserSchema", only=["id_user", "first_name", "last_name", "email"])
    company = fields.Nested("CompanySchema", only=["id_company", "name_company", "email_company"])
    license_mode = fields.Nested("LicenseModeSchema", only=["id_license_mode", "name"])
    access_rights = fields.Nested("AccessRightsSchema", only=["id_access_right", "name"])


class PaymentMethodSchema(BaseSchema):
    class Meta:
        model = PaymentMethod
        #load_instance = True
        include_fk = True

class OfferTypeSchema(BaseSchema):
    class Meta:
        model = OfferTypes
        #load_instance = True

class LoginHistorySchema(BaseSchema):
    user_id = fields.Integer(required=True)
    class Meta:
        model = LoginHistory
        #load_instance = True
        include_fk = True

class OAuthProviderSchema(BaseSchema):
    class Meta:
        model = OAuthProvider
        #load_instance = True

class UserOAuthSchema(BaseSchema):
    user_id = fields.Integer(required=True)
    provider_id = fields.Integer(required=True)

    class Meta:
        model = UserOAuth
        #load_instance = True

class UserSessionSchema(BaseSchema):
    user_id = fields.Integer(required=True)
    class Meta:
        model = UserSession
        #load_instance = True

class LogUserActionSchema(BaseSchema):
    user_id = fields.Integer(required=True)
    class Meta:
        model = LogUserAction
        #load_instance = True
        
class FonctionCompanySchema(BaseSchema):
    class Meta:
        model = FonctionCompany
        #load_instance = True
        include_relationships = False
        include_fk = True

    company = fields.Nested("CompanySchema", only=("id_company", "name_company"))
    user = fields.Nested("UserSchema", only=("id_user", "first_name", "last_name"))
    permission = fields.Nested("PermissionSSOSchema", only=("id_permission", "permission_name"))

