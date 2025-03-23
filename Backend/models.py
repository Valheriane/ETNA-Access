import datetime
from datetime import datetime, date, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()

db = SQLAlchemy(model_class=Base)

class Product(Base):
    __tablename__ = 'products'

    id_product = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    type = Column(String(50), nullable=False)
    target_audience = Column(String(50), nullable=False)
    demo_link = Column(String(255))
    why_use = Column(String(255))
    advantages = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    updated_at = Column(DateTime, default=datetime.now)
    
    offer_products = relationship("OfferProducts", back_populates="product")
    product_imgs = relationship("ProductImgs", back_populates="product")
    licenses = relationship("License", back_populates="product")
    configurations = relationship("ProductConfigurations", back_populates="product")

class Offer(Base):
    __tablename__ = 'offers'

    id_offer = Column(Integer, primary_key=True, index=True)
    offer_type_id = Column(Integer, ForeignKey('offer_types.id_offer_type'), nullable=False)
    offer_name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    license_mode_id = Column(Integer, ForeignKey('license_modes.id_license_mode'), nullable=False)
    target_audience = Column(String(50), nullable=False)
    offer_advantages = Column(String(255))
    offer_duration = Column(Integer)
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    updated_at = Column(DateTime, default=datetime.now)
    access_rights_id = Column(Integer, ForeignKey('access_rights.id_access_right'), nullable=False)

    offer_type = relationship("OfferTypes", back_populates="offer")
    license_mode = relationship("LicenseMode", back_populates="offers")
    offer_products = relationship("OfferProducts", back_populates="offer")
    access_rights = relationship("AccessRights", back_populates="offers")

class OfferProducts(Base):
    __tablename__ = 'offer_products'

    id_offer_products = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer, ForeignKey('offers.id_offer'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id_product'), nullable=False)
    access_count = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    updated_at = Column(DateTime, default=datetime.now)

    offer = relationship("Offer", back_populates="offer_products")
    product = relationship("Product", back_populates="offer_products")

    __table_args__ = (
        UniqueConstraint('offer_id', 'product_id', name='uix_offer_product'),
    )

class Images(Base):
    __tablename__ = 'images'

    id_image = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), nullable=False)
    type_imgs_id = Column(Integer, ForeignKey('type_imgs.id_type_img'), nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    updated_at = Column(DateTime, default=datetime.now)

    type_imgs = relationship("TypeImgs", back_populates="images")

class ProductImgs(Base):
    __tablename__ = 'product_imgs'

    id_product_img = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id_product'),  nullable=False)
    imgs_id = Column(Integer, ForeignKey('images.id_image'),  nullable=False)
    primary_imgs = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    updated_at = Column(DateTime, default=datetime.now)

    product = relationship("Product", back_populates="product_imgs")
    image = relationship("Images")

    __table_args__ = (
        UniqueConstraint('product_id', 'imgs_id', name='uix_product_img'),
    )

class ProductConfigurations(Base):
    __tablename__ = 'product_configurations'

    id_product_configuration = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id_product'), nullable=False)
    config_type = Column(Integer)
    operating_system = Column(String(255))
    processor = Column(String(255))
    ram = Column(String(255))
    storage = Column(String(255))
    gpu = Column(String(255))
    internet_connection = Column(String(255))
    supported_browsers = Column(String(255))
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    updated_at = Column(DateTime, default=datetime.now)

    product = relationship("Product", back_populates="configurations")

class License(Base):
    __tablename__ = 'licenses'

    id_license = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('company.id_company'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id_user'), nullable=True)
    product_id = Column(Integer, ForeignKey('products.id_product'), nullable=False)
    license_mode_id = Column(Integer, ForeignKey('license_modes.id_license_mode'), nullable=False)
    start_date = Column(DateTime, default=datetime.now, nullable=False)
    end_date = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    updated_at = Column(DateTime, default=datetime.now)
    active = Column(Boolean, nullable=False)
    access_rights_id = Column(Integer, ForeignKey('access_rights.id_access_right'), nullable=False)
    
    product = relationship("Product", back_populates="licenses")
    user = relationship("Users", back_populates="licenses")
    company = relationship("Company", back_populates="licenses")
    license_mode = relationship("LicenseMode", back_populates="licenses")
    access_rights = relationship("AccessRights", back_populates="licenses")

class Users(Base):
    __tablename__ = 'users'
    
    id_user = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(18), nullable=False)
    phone_prefix_user = Column(String(5), nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    updated_at = Column(DateTime, default=datetime.now)
    imgs_id = Column(Integer, ForeignKey('images.id_image'), nullable=False)
    statut = Column(Integer, nullable=False) #1=actif , 2=deactive , 3=supprimer
    
    # Relations
    licenses = relationship("License", back_populates="user", cascade=None)
    addresses = relationship("Address", back_populates="user", cascade=None)
    fonctions = relationship("FonctionCompany", back_populates="user", cascade="all, delete-orphan")  # Lien vers FonctionCompany
    user_logs = relationship("LogUserAction", back_populates="user", cascade=None)
    payment_methods = relationship("PaymentMethod", back_populates="user", cascade=None)
    login_history = relationship("LoginHistory", back_populates="user", cascade=None)
    user_oauth = relationship("UserOAuth", back_populates="user", cascade=None)
    sessions = relationship("UserSession", back_populates="user", cascade=None)

class Company(Base):
    __tablename__ = 'company'
    
    id_company = Column(Integer, primary_key=True, index=True)
    name_company = Column(String(255), nullable=False)
    imgs_id = Column(Integer, ForeignKey('images.id_image'), nullable=False)
    email_company = Column(String(255), nullable=False, unique=True)
    company_phone = Column(String(18), nullable=False)
    phone_prefix_company = Column(String(5), nullable=False)
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    updated_at = Column(DateTime, default=datetime.now)
    national_id = Column(String(50), nullable=True)
    registry_type = Column(String(50), nullable=True)
    country_code = Column(String(2), nullable=True)
    website = Column(String(255), nullable=True)

    # Relations
    licenses = relationship("License", back_populates="company")
    image = relationship("Images")
    addresses = relationship("Address", back_populates="company")
    fonctions = relationship("FonctionCompany", back_populates="company")  # Lien vers FonctionCompany
    payment_methods = relationship("PaymentMethod", back_populates="company")

class PermissionSSO(Base):
    __tablename__ = 'permission_sso'
    
    id_permission = Column(Integer, primary_key=True, index=True)
    permission_name = Column(String(50), nullable=False)
    permission_description = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    updated_at = Column(DateTime, default=datetime.now)

class FonctionCompany(Base):
    __tablename__ = 'fonction_company'
    
    id_fonction_company = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('company.id_company'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id_user'), nullable=False)
    fonction = Column(String(255), nullable=True)  # La fonction de l'utilisateur dans l'entreprise
    permission_id = Column(Integer, ForeignKey('permission_sso.id_permission'), nullable=False)
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    updated_at = Column(DateTime, default=datetime.now)

    # Relations
    company = relationship("Company", back_populates="fonctions")
    user = relationship("Users", back_populates="fonctions")
    permission = relationship("PermissionSSO")  
    
    # Contrainte d'unicité sur user_id
    __table_args__ = (UniqueConstraint('user_id', name='_user_id_uc'),)

class Address(Base):
    __tablename__ = 'addresses'

    id_address  = Column(Integer, primary_key=True, index=True)
    address_line_1 = Column(String(255), nullable=False)
    address_line_2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    state_province = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id_user'), nullable=True)
    company_id = Column(Integer, ForeignKey('company.id_company'), nullable=True)
    invoice_date = Column(DateTime, default=datetime.now)
    is_billing = Column(Boolean, default=True)  # Indique si c'est une adresse de facturation
    address_type = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relations
    user = relationship("Users", back_populates="addresses")
    company = relationship("Company", back_populates="addresses")
    payment_methods = relationship("PaymentMethod", back_populates="addresses")

class PaymentMethod(Base):
    __tablename__ = 'payment_methods'

    id_payment_method = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id_user'), nullable=True)
    company_id = Column(Integer, ForeignKey('company.id_company'), nullable=True)
    provider = Column(String(50), nullable=False)
    payment_type = Column(String(50), nullable=False)
    last_four_digits = Column(String(4))
    expiration_date = Column(DateTime, default=datetime.now, nullable=True)
    billing_address_id = Column(Integer, ForeignKey('addresses.id_address'), nullable=True)  # Mise à jour du nom pour correspondre
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True)

    user = relationship("Users", back_populates="payment_methods")
    company = relationship("Company", back_populates="payment_methods")
    addresses = relationship("Address", back_populates="payment_methods")
    
class LicenseMode(Base):
    __tablename__ = 'license_modes'

    id_license_mode = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    offers = relationship("Offer", back_populates="license_mode")
    licenses = relationship("License", back_populates="license_mode")

class OfferTypes(Base):
    __tablename__ = 'offer_types'

    id_offer_type = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    offer = relationship("Offer", back_populates="offer_type")

class AccessRights(Base):
    __tablename__ = 'access_rights'
    
    id_access_right = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    offers = relationship("Offer", back_populates="access_rights") 
    licenses = relationship("License", back_populates="access_rights")

class TypeImgs(Base):
    __tablename__ = 'type_imgs'

    id_type_img = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    images = relationship("Images", back_populates="type_imgs")

class LoginHistory(Base):
    __tablename__ = 'login_history'
    
    id_login_history = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id_user'), nullable=True)
    login_time = Column(DateTime, default=datetime.now)
    logout_time = Column(DateTime, default=datetime.now)
    ip_address = Column(String(45))  # Peut gérer IPv4 et IPv6
    device_info = Column(String(255))  # Info sur le navigateur ou l'appareil
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    user = relationship("Users", back_populates="login_history")

class OAuthProvider(Base):
    __tablename__ = 'oauth_providers'
    
    id_oauth_provider = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String(50), nullable=False)
    client_id = Column(String(255), nullable=False)
    client_secret = Column(String(255), nullable=False)
    redirect_uri = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    oauth_accounts = relationship("UserOAuth", back_populates="provider")

class UserOAuth(Base):
    __tablename__ = 'user_oauths'
    
    id_user_oauth = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id_user'), nullable=True)
    provider_id = Column(Integer, ForeignKey('oauth_providers.id_oauth_provider'), nullable=False)
    provider_user_id = Column(String(255), nullable=False)
    access_token = Column(String(255))
    refresh_token = Column(String(255))
    access_token_expiration = Column(DateTime, default=datetime.now)
    refresh_token_expiration = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)  # Optionnel, pour suivre le statut du compte OAuth
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("Users", back_populates="user_oauth")
    provider = relationship("OAuthProvider", back_populates="oauth_accounts")

class UserSession(Base):
    __tablename__ = 'user_sessions'
    
    id_user_session = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id_user'), nullable=True)
    session_token = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    expires_at = Column(DateTime, default=datetime.now, nullable=False)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    user = relationship("Users", back_populates="sessions")

class LogUserAction(Base):
    __tablename__ = 'user_logs'
 
    id_log = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id_user'), nullable=True)
    action = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_navweb = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now, onupdate=None)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
 
    user = relationship("Users", back_populates="user_logs")
 

