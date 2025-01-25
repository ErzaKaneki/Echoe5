# Create your tests here.

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
import json

class APIAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123!'
        )
        self.login_url = '/api/v1/auth/login/'
        self.post_url = '/api/v1/posts/'

    def test_login_success(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123!'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpass'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_access(self):
        # Login first
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123!'
        }, format='json')
        
        # Set token in header
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )
        
        # Try accessing protected endpoint
        response = self.client.get(self.post_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)