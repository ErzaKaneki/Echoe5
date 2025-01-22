# Create your tests here.

from django.urls import reverse
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from social_django.models import UserSocialAuth
from unittest.mock import patch

@override_settings(
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY='test_key',
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET='test_secret'
)

class SocialAuthTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_google_login_url(self):
        response = self.client.get(reverse('social:begin', args=['google-oauth2']))
        self.assertEqual(response.status_code, 302)  # Should redirect to Google
        
    @patch('social_core.backends.google.GoogleOAuth2.do_auth')
    def test_google_auth_complete(self, mock_do_auth):
        # Mock successful authentication
        mock_do_auth.return_value = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = self.client.get(reverse('social:complete', args=['google-oauth2']))
        self.assertEqual(response.status_code, 302)  # Should redirect to success URL
        
    def test_social_auth_failure(self):
        response = self.client.get(reverse('social:complete', args=['google-oauth2']))
        self.assertEqual(response.status_code, 302)  # Should redirect to failure URL

class LandingPageTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_landing_page_load(self):
        response = self.client.get('/')  # Test by path instead of reverse
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/landing_page.html')