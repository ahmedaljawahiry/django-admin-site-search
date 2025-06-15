"""Pytest config and fixtures, for "unit" tests that run without a browser"""

import pytest
from django.contrib.auth.models import User
from django.test.client import Client


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Auto-enable DB access for all tests: https://pytest-django.readthedocs.io/en/latest/helpers.html#db"""
    pass


@pytest.fixture()
def user_standard(client):
    """An authenticated user"""
    user = User.objects.create_user(username="standard-user", password="not-a-secret")
    client.force_login(user)
    return user


@pytest.fixture()
def user_admin(client, admin_user):
    """An authenticated admin user"""
    user = User.objects.create_user(
        username="admin-user", password="not-a-secret-1", is_staff=True
    )
    client.force_login(user)
    return user


@pytest.fixture()
def user_super(client):
    """An authenticated superuser"""
    user = User.objects.create_user(
        username="superuser", password="not-a-secret-2", is_superuser=True
    )
    client.force_login(user)
    return user


@pytest.fixture()
def client_standard(user_standard):
    """A client for a standard, authenticated, user"""
    # don't use the client fixture since other fixtures use it to log users in
    client = Client()
    client.force_login(user_standard)
    return client


@pytest.fixture()
def client_admin(user_admin):
    """A client for an authenticated admin user"""
    # don't use the client fixture since other fixtures use it to log users in
    client = Client()
    client.force_login(user_admin)
    return client


@pytest.fixture()
def client_super(user_super):
    """A client for an authenticated superuser"""
    # don't use the client fixture since other fixtures use it to log users in
    client = Client()
    client.force_login(user_super)
    return client


@pytest.fixture()
def client_unauthenticated():
    """Returns a client that is logged out"""
    client = Client()
    client.logout()
    return client


@pytest.fixture()
def client_super_admin(client_admin, user_admin):
    """Returns a client for a user that is marked as staff and superuser, i.e. can view all
    models."""
    user_admin.is_superuser = True
    user_admin.save()

    return client_admin
