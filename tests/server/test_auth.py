"""Tests verifying API access and authorization, for the search/ endpoint"""

import pytest
from django.contrib.auth.models import Permission

from dev.football.players.factories import PlayerFactory
from dev.football.stadiums.factories import StadiumFactory
from dev.football.teams.factories import TeamFactory
from tests import request_search

# It shouldn't make a difference, but check all auth scenarios for each search method
pytestmark = pytest.mark.parametrize(
    "site_search_method", ["model_char_fields", "admin_search_fields"]
)


@pytest.mark.parametrize(
    "is_staff, is_superuser, status_code",
    [(False, False, 302), (False, True, 302), (True, False, 200), (True, True, 200)],
)
def test_authenticated(
    client_standard,
    user_standard,
    is_staff,
    is_superuser,
    status_code,
    site_search_method,
):
    """Verify that only staff users can access the API"""
    user_standard.is_staff = is_staff
    user_standard.is_superuser = is_superuser
    user_standard.save()

    response = request_search(client_standard, site_search_method=site_search_method)

    assert response.status_code == status_code


def test_unauthenticated(client_admin, site_search_method):
    """Verify that unauthenticated users cannot access the API"""
    client_admin.logout()
    response = request_search(client_admin, site_search_method=site_search_method)

    assert response.status_code == 302


@pytest.mark.parametrize(
    "permissions, can_add",
    [
        (["view_team"], False),
        (["change_team"], False),
        (["view_team", "change_team"], False),
        (["view_team", "add_team"], True),
        (["view_team", "change_team", "add_team"], True),
    ],
)
def test_permission_can_view(
    client_admin, user_admin, permissions, can_add, site_search_method
):
    """Verify that users with view_ or change_ permission can view the app,
    model, and objects. The value of url_add, for a model, is included if the
    user has the add_ permission"""
    obj = TeamFactory(name="abcd")

    permission_ids = Permission.objects.filter(codename__in=permissions).values_list(
        "id", flat=True
    )
    user_admin.user_permissions.add(*permission_ids)

    response = request_search(
        client_admin, query="abcd", site_search_method=site_search_method
    )
    data = response.json()

    assert response.status_code == 200
    assert len(data["results"]["apps"]) == 1
    assert data["results"]["apps"][0]["id"] == "teams"
    assert len(data["results"]["apps"][0]["models"]) == 1
    assert data["results"]["apps"][0]["models"][0]["id"] == "teams.Team"
    assert (data["results"]["apps"][0]["models"][0]["url_add"] is not None) is can_add
    assert len(data["results"]["apps"][0]["models"][0]["objects"]) == 1
    assert data["results"]["apps"][0]["models"][0]["objects"][0]["id"] == str(obj.id)
    assert data["counts"] == {"apps": 1, "models": 1, "objects": 1}


@pytest.mark.parametrize(
    "permissions", [[], ["add_team"], ["delete_team"], ["add_team", "delete_team"]]
)
def test_permission_cannot_view(
    client_admin, user_admin, permissions, site_search_method
):
    """Verify that users without the view_model permission cannot view the app, model,
    or objects. Other permissions have no effect."""
    TeamFactory(name="abcd")

    permission_ids = Permission.objects.filter(codename__in=permissions).values_list(
        "id", flat=True
    )
    user_admin.user_permissions.add(*permission_ids)

    response = request_search(
        client_admin, query="abcd", site_search_method=site_search_method
    )
    data = response.json()

    assert response.status_code == 200
    assert len(data["results"]["apps"]) == 0
    assert data["counts"] == {"apps": 0, "models": 0, "objects": 0}


@pytest.mark.parametrize("factory", [PlayerFactory, StadiumFactory])
def test_permission_can_view_other(
    client_admin, user_admin, factory, site_search_method
):
    """Verify that permissions are checked for each model, in each app"""
    factory(name="other model, in same app")

    permissions = ["view_team", "change_team", "add_team"]
    permission_ids = Permission.objects.filter(codename__in=permissions).values_list(
        "id", flat=True
    )
    user_admin.user_permissions.add(*permission_ids)

    response = request_search(
        client_admin, query="other", site_search_method=site_search_method
    )
    data = response.json()

    assert response.status_code == 200
    assert len(data["results"]["apps"]) == 0
    assert data["counts"] == {"apps": 0, "models": 0, "objects": 0}


def test_admin_not_registered(client_super_admin, site_search_method):
    """Verify results are not returned for models that are not registered with
    the admin site"""
    # Permission model isn't registered with the admin, by default
    objects = Permission.objects.filter(codename__startswith="view_")

    response = request_search(
        client_super_admin, query="view", site_search_method=site_search_method
    )
    data = response.json()

    assert len(objects) > 0
    assert response.status_code == 200
    assert len(data["results"]["apps"]) == 0
    assert data["counts"] == {"apps": 0, "models": 0, "objects": 0}
