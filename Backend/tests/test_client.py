import unittest
from app import app  # Import de ton app Flask

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()  # Simule un client HTTP

    def test_get_products(self):
        response = self.client.get('/api/products')  # Appelle la route
        self.assertEqual(response.status_code, 200)  # Vérifie le statut
        data = response.get_json()
        self.assertIsInstance(data, list)  # Vérifie que la réponse est une liste

    def test_post_product(self):
        product_data = {
            "name": "Test Product",
            "version": "1.0",
            "type": "Software",
            "target_audience": "Developers"
        }
        response = self.client.post('/api/products', json=product_data)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['name'], "Test Product")

if __name__ == '__main__':
    unittest.main()
