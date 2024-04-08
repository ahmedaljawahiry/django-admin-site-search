"""Verify that overrideable functions, in the view, are invoked correctly"""
from unittest.mock import patch, MagicMock

from django.contrib.auth.models import Permission, User
from django.test import Client

from dev.football.stadiums.models import Stadium
from dev.football.teams.models import Team
from tests import request_search


def request_with_patch(client: Client, user: User, method_name: str) -> MagicMock:
    """Requests a search, with the given method patched. The user is set up with access to the
    Team and Stadium models"""
    permission_ids = Permission.objects.filter(codename__in=["view_team", "view_stadium"]).values_list(
        "id", flat=True
    )
    user.user_permissions.add(*permission_ids)

    with patch(f"dev.admin.CustomAdminSite.{method_name}") as patch_method:
        request_search(client, query="QuEry")

    return patch_method


def test_match_apps(client_admin, user_admin):
    """Verify the match_app method is correctly invoked for each app that the user has access to"""
    patch_match_app = request_with_patch(client_admin, user_admin, "match_app")
    call_args_list = [c[0] for c in patch_match_app.call_args_list]

    assert len(call_args_list) == 2
    assert ("QuEry", "Stadiums") in call_args_list
    assert ("QuEry", "Teams") in call_args_list


def test_match_model(client_admin, user_admin):
    """Verify the match_model method is correctly invoked for each model that the user has access to"""
    patch_match_model = request_with_patch(client_admin, user_admin, "match_model")
    call_args_list = [c[0] for c in patch_match_model.call_args_list]

    assert len(call_args_list) == 2
    assert ("QuEry", "Stadiums", "Stadium", Stadium._meta.get_fields()) in call_args_list
    assert ("QuEry", "Teams", "Team", Team._meta.get_fields()) in call_args_list


def test_match_objects(client_admin, user_admin):
    """Verify the match_objects method is correctly invoked for each model that the user has access to"""
    patch_match_objects = request_with_patch(client_admin, user_admin, "match_objects")
    call_args_list = [c[0] for c in patch_match_objects.call_args_list]

    assert len(call_args_list) == 2
    assert ("QuEry", Stadium, Stadium._meta.get_fields()) in call_args_list
    assert ("QuEry", Team, Team._meta.get_fields()) in call_args_list


def test_filter_field(client_admin, user_admin):
    """Verify the filter_field method is correctly invoked for each field, on each model, that the user
    has access to"""
    patch_field_fields = request_with_patch(client_admin, user_admin, "filter_field")
    call_args_list = [c[0] for c in patch_field_fields.call_args_list]
    expected_fields = Stadium._meta.get_fields() + Team._meta.get_fields()

    assert len(call_args_list) == len(expected_fields)
    for field in expected_fields:
        # query should be passed in as-is (regression: was previously passed in as .lower())
        assert ("QuEry", field) in call_args_list
