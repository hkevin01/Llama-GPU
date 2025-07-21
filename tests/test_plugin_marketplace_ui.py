import unittest
from src.plugin_marketplace_ui import app

class TestPluginMarketplaceUI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
    def test_health(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertIn('ok', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
