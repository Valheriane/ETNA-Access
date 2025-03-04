import logging
from flask import Flask
from faker import Faker



app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
# Initialisation de Faker
fake = Faker()

@app.before_request
def test_function():
    print("This runs before the first request.")

@app.route("/")
def home():
    return "Hello, World!"


@app.route("/test_faker")
def testFaker():
    """Route pour tester Faker et afficher un nom généré"""
    generated_name = fake.name()  # Utilisation de Faker pour générer un nom
    print(f"Nom généré par Faker : {generated_name}")  # Affichage du nom généré dans la console
    return f"Nom généré par Faker : {generated_name}"  # Affiche également le nom dans la réponse HTTP

if __name__ == "__main__":
    app.run(debug=True)
