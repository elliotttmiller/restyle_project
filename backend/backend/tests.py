"""
Tests for backend health endpoints and admin user functionality.
"""
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.http import JsonResponse


class HealthEndpointTests(TestCase):
    """Test health check endpoints."""
    
    def setUp(self):
        self.client = Client()
    
    def test_health_endpoint_exists(self):
        """Test that the /health/ endpoint exists and returns 200."""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
    
    def test_health_endpoint_returns_json(self):
        """Test that the /health/ endpoint returns valid JSON."""
        response = self.client.get('/health/')
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Parse the JSON to ensure it's valid
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_simple_health_endpoint(self):
        """Test that the /health endpoint (without trailing slash) works."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_health_endpoint_contains_required_fields(self):
        """Test that health endpoint contains required fields."""
        response = self.client.get('/health/')
        data = json.loads(response.content)
        
        required_fields = ['status', 'service', 'timestamp']
        for field in required_fields:
            self.assertIn(field, data)
        
        self.assertEqual(data['service'], 'restyle-backend')
    
    def test_root_endpoint_health(self):
        """Test that the root endpoint also returns healthy status."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')


class AdminUserCreationTests(TestCase):
    """Test admin user creation functionality."""
    
    def setUp(self):
        self.User = get_user_model()
    
    def test_create_prod_superuser_command_exists(self):
        """Test that the create_prod_superuser management command exists."""
        try:
            call_command('create_prod_superuser')
        except Exception as e:
            # The command should run without errors
            self.fail(f"create_prod_superuser command failed: {e}")
    
    def test_create_prod_superuser_creates_user(self):
        """Test that the management command creates the expected user."""
        # Ensure user doesn't exist initially
        self.assertFalse(
            self.User.objects.filter(username='elliotttmiller').exists()
        )
        
        # Run the command
        call_command('create_prod_superuser')
        
        # Check that user was created
        self.assertTrue(
            self.User.objects.filter(username='elliotttmiller').exists()
        )
        
        # Check user properties
        user = self.User.objects.get(username='elliotttmiller')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password('elliott'))
    
    def test_create_prod_superuser_updates_existing_user(self):
        """Test that the command updates an existing user."""
        # Create a user with wrong permissions
        user = self.User.objects.create_user(
            username='elliotttmiller',
            email='elliotttmiller@example.com',
            password='wrongpassword'
        )
        user.is_staff = False
        user.is_superuser = False
        user.save()
        
        # Run the command
        call_command('create_prod_superuser')
        
        # Refresh from database
        user.refresh_from_db()
        
        # Check that user was updated
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password('elliott'))
    
    def test_admin_user_login(self):
        """Test that the created admin user can log in."""
        # Create the admin user
        call_command('create_prod_superuser')
        
        # Test login
        login_successful = self.client.login(
            username='elliotttmiller', 
            password='elliott'
        )
        self.assertTrue(login_successful)
        
        # Test access to admin
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)