import unittest
import json
from app import app
import db

class TestPublicSpace360(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_pages_render(self):
        pages = [
            '/',
            '/login',
            '/register',
            '/map',
            '/spaces',
            '/spaces/1',
            '/survey',
            '/results',
            '/report',
            '/about',
            '/contact',
            '/admin/login'
        ]
        for url in pages:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Page {url} failed with status {response.status_code}")
            print(f"[OK] Page {url} returned 200 OK")

    def test_api_stats(self):
        res = self.client.get('/api/stats')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('total_spaces', data)
        self.assertIn('total_surveys', data)
        print(f"[OK] /api/stats verified: {data['total_spaces']} spaces, {data['total_surveys']} surveys")

    def test_api_spaces(self):
        res = self.client.get('/api/spaces')
        self.assertEqual(res.status_code, 200)
        spaces = res.get_json()
        self.assertGreater(len(spaces), 0)
        print(f"[OK] /api/spaces verified: {len(spaces)} spaces returned")

    def test_api_analytics(self):
        res = self.client.get('/api/analytics')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('usage_by_type', data)
        self.assertIn('activities', data)
        self.assertIn('facility_ratings', data)
        print("[OK] /api/analytics verified with complete dynamic chart telemetry")

    def test_user_flow(self):
        # 1. Register new user
        import random
        rnd = random.randint(1000, 9999)
        test_email = f"testcitizen_{rnd}@example.com"
        reg_data = {
            'name': 'Test Citizen',
            'email': test_email,
            'mobile': '+91 99999 88888',
            'password': 'password123',
            'confirm_password': 'password123',
            'age_group': '18–25',
            'gender': 'Female'
        }
        res = self.client.post('/api/register', json=reg_data)
        self.assertEqual(res.status_code, 201)
        print("[OK] /api/register verified successfully")

        # 2. Login
        login_data = {
            'email': test_email,
            'password': 'password123'
        }
        res = self.client.post('/api/login', json=login_data)
        self.assertEqual(res.status_code, 200)
        print("[OK] /api/login verified successfully")

        # 3. Access User Dashboard
        dash_res = self.client.get('/dashboard')
        self.assertEqual(dash_res.status_code, 200)
        print("[OK] /dashboard authenticated successfully")

        # 4. Submit Survey
        survey_payload = {
            'space_id': 1,
            'visit_frequency': 'Daily',
            'purpose': 'Walking',
            'age_group': '18–25',
            'safety_rating': 5,
            'cleanliness_rating': 5,
            'lighting_rating': 4,
            'seating_rating': 4,
            'water_rating': 4,
            'accessibility_rating': 5,
            'improvement': 'Drinking Water',
            'suggestion': 'Automated unit test survey entry'
        }
        res = self.client.post('/api/surveys', json=survey_payload)
        self.assertEqual(res.status_code, 201)
        print("[OK] /api/surveys submission verified successfully")

    def test_admin_flow(self):
        # 1. Admin Login
        res = self.client.post('/api/admin/login', json={
            'email': 'admin@publicspace360.org',
            'password': 'admin123'
        })
        self.assertEqual(res.status_code, 200)
        print("[OK] /api/admin/login verified successfully")

        # 2. Admin Dashboard
        res = self.client.get('/admin/dashboard')
        self.assertEqual(res.status_code, 200)
        print("[OK] /admin/dashboard loaded successfully")

if __name__ == '__main__':
    unittest.main()
