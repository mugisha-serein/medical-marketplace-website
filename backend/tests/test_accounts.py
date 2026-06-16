import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .factories import UserFactory, VendorProfileFactory, CustomerProfileFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer_user(db):
    user = UserFactory(is_vendor=False)
    CustomerProfileFactory(user=user)
    return user


@pytest.fixture
def vendor_user(db):
    from tests.factories import VendorUserFactory
    return VendorUserFactory()


@pytest.fixture
def auth_client(api_client, customer_user):
    api_client.force_authenticate(user=customer_user)
    return api_client, customer_user


@pytest.mark.django_db
class TestRegistration:

    def test_register_customer_success(self, api_client):
        payload = {
            'email': 'newcustomer@test.com',
            'password': 'SecurePass123',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'customer',
        }
        resp = api_client.post(reverse('auth-register'), payload)
        assert resp.status_code == status.HTTP_201_CREATED
        assert 'user_id' in resp.data

    def test_register_vendor_success(self, api_client):
        payload = {
            'email': 'vendor@test.com',
            'password': 'SecurePass123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': 'vendor',
            'company_name': 'MedTech Solutions',
        }
        resp = api_client.post(reverse('auth-register'), payload)
        assert resp.status_code == status.HTTP_201_CREATED

    def test_register_vendor_without_company_name_fails(self, api_client):
        payload = {
            'email': 'vendor2@test.com',
            'password': 'SecurePass123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': 'vendor',
        }
        resp = api_client.post(reverse('auth-register'), payload)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert 'company_name' in str(resp.data)

    def test_register_duplicate_email_fails(self, api_client, customer_user):
        payload = {
            'email': customer_user.email,
            'password': 'SecurePass123',
            'first_name': 'A',
            'last_name': 'B',
            'role': 'customer',
        }
        resp = api_client.post(reverse('auth-register'), payload)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_weak_password_fails(self, api_client):
        payload = {
            'email': 'weak@test.com',
            'password': '123',
            'first_name': 'A',
            'last_name': 'B',
            'role': 'customer',
        }
        resp = api_client.post(reverse('auth-register'), payload)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestAuthentication:

    def test_login_success_returns_tokens(self, api_client, customer_user):
        resp = api_client.post(reverse('auth-token'), {
            'email': customer_user.email,
            'password': 'testpass123',
        })
        assert resp.status_code == status.HTTP_200_OK
        assert 'access' in resp.data
        assert 'refresh' in resp.data
        assert resp.data['role'] == 'customer'

    def test_login_wrong_password(self, api_client, customer_user):
        resp = api_client.post(reverse('auth-token'), {
            'email': customer_user.email,
            'password': 'wrongpassword',
        })
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, api_client):
        resp = api_client.post(reverse('auth-token'), {
            'email': 'nobody@test.com',
            'password': 'somepassword',
        })
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_endpoint_returns_user(self, auth_client):
        client, user = auth_client
        resp = client.get(reverse('auth-me'))
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['email'] == user.email
        assert resp.data['role'] == 'customer'

    def test_me_endpoint_unauthenticated(self, api_client):
        resp = api_client.get(reverse('auth-me'))
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_blacklists_token(self, api_client, customer_user):
        # Get tokens
        login = api_client.post(reverse('auth-token'), {
            'email': customer_user.email,
            'password': 'testpass123',
        })
        refresh = login.data['refresh']
        access = login.data['access']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

        # Logout
        resp = api_client.post(reverse('auth-logout'), {'refresh': refresh})
        assert resp.status_code == status.HTTP_200_OK

        # Try to use refresh token again — should fail
        resp2 = api_client.post(reverse('auth-token-refresh'), {'refresh': refresh})
        assert resp2.status_code == status.HTTP_401_UNAUTHORIZED

    def test_vendor_role_returned_in_jwt(self, api_client, vendor_user):
        resp = api_client.post(reverse('auth-token'), {
            'email': vendor_user.email,
            'password': 'testpass123',
        })
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['role'] == 'vendor'


@pytest.mark.django_db
class TestProfileEndpoints:

    def test_update_own_name(self, auth_client):
        client, user = auth_client
        resp = client.patch(reverse('auth-me'), {'first_name': 'Updated'})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['first_name'] == 'Updated'

    def test_change_password_success(self, auth_client):
        client, user = auth_client
        resp = client.post(reverse('auth-change-password'), {
            'old_password': 'testpass123',
            'new_password': 'NewSecurePass456',
        })
        assert resp.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password('NewSecurePass456')

    def test_change_password_wrong_old(self, auth_client):
        client, _ = auth_client
        resp = client.post(reverse('auth-change-password'), {
            'old_password': 'wrongcurrent',
            'new_password': 'NewSecurePass456',
        })
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
