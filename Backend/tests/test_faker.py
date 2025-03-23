from faker import Faker
from flask_jwt_extended import jwt_required, get_jwt_identity
import sys

fake = Faker()
print(fake.name())



print("flask-jwt-extended importé avec succès !")


print(sys.executable)
print(sys.version)
