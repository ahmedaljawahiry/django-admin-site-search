"""Tests verifying the API response"""

from unittest.mock import patch

import pytest
from django.apps import apps
from django.test import override_settings

from admin_site_search.views import AdminSiteSearchView
from dev.football.core.factories import GroupFactory
from dev.football.players.factories import PlayerAttributesFactory, PlayerFactory
from dev.football.stadiums.factories import StadiumFactory
from dev.football.teams.factories import TeamFactory
from tests import request_search


def test_empty(client_admin):
    """Verify the fields of an empty response, i.e. no matches"""
    response = request_search(client_admin, query="xyz")
    data = response.json()

    assert response.status_code == 200
    assert len(data.keys()) == 3
    assert data["results"] == {"apps": []}
    assert data["counts"] == {"apps": 0, "models": 0, "objects": 0}
    assert not data["errors"]


def test_apps(client_super_admin):
    """Verify the fields of a response with an app result"""
    response = request_search(client_super_admin, query="authentication")
    data = response.json()

    assert response.status_code == 200
    assert len(data.keys()) == 3
    assert data["results"] == {
        "apps": [
            {
                "id": "auth",
                "name": "Authentication and Authorization",
                "url": "/admin/auth/",
                "models": [],
            }
        ]
    }
    assert data["counts"] == {"apps": 1, "models": 0, "objects": 0}
    assert not data["errors"]


def test_models(client_super_admin):
    """Verify the fields of a response with a model result"""
    response = request_search(client_super_admin, query="capacity")
    data = response.json()

    assert response.status_code == 200
    assert data["results"] == {
        "apps": [
            {
                "id": "stadiums",
                "name": "Stadiums",
                "url": "/admin/stadiums/",
                "models": [
                    {
                        "id": "stadiums.Stadium",
                        "name": "Stadiums",
                        "url": "/admin/stadiums/stadium/",
                        "url_add": "/admin/stadiums/stadium/add/",
                        "objects": [],
                    }
                ],
            }
        ]
    }
    assert data["counts"] == {"apps": 1, "models": 1, "objects": 0}
    assert not data["errors"]


def test_model_class_none(client_super_admin):
    """Verify models for which no class is found, are skipped.

    Context: some packages register unexpected config with the admin,
    e.g. https://github.com/ahmedaljawahiry/django-admin-site-search/issues/6"""
    with patch.object(AdminSiteSearchView, "get_model_class") as get_model_class:
        get_model_class.return_value = None

        response = request_search(client_super_admin, query="stadium")
        data = response.json()

    assert response.status_code == 200
    assert data["results"] == {
        "apps": [
            {
                "id": "stadiums",
                "name": "Stadiums",
                "url": "/admin/stadiums/",
                "models": [],
            }
        ]
    }
    assert data["counts"] == {"apps": 1, "models": 0, "objects": 0}
    assert not data["errors"]


def test_objects(client_super_admin):
    """Verify the fields of a response with an object result"""
    match = GroupFactory(name="Internal testers")

    response = request_search(client_super_admin, query="internal")
    data = response.json()

    assert response.status_code == 200
    assert data["results"] == {
        "apps": [
            {
                "id": "auth",
                "name": "Authentication and Authorization",
                "url": "/admin/auth/",
                "models": [
                    {
                        "id": "auth.Group",
                        "name": "Groups",
                        "url": "/admin/auth/group/",
                        "url_add": "/admin/auth/group/add/",
                        "objects": [
                            {
                                "id": str(match.id),
                                "name": str(match),
                                "url": f"/admin/auth/group/{match.id}",
                            }
                        ],
                    }
                ],
            }
        ]
    }
    assert data["counts"] == {"apps": 1, "models": 1, "objects": 1}
    assert not data["errors"]


def test_objects_one_to_one_pk(client_super_admin):
    """Verify no errors for models with a OneToOne primary key field (i.e. no .id attribute)"""
    # primary key is player, so .id won't work
    match = PlayerAttributesFactory(nationality="British")

    response = request_search(client_super_admin, query="british")
    data = response.json()

    assert response.status_code == 200
    assert data["results"] == {
        "apps": [
            {
                "id": "players",
                "name": "Players",
                "url": "/admin/players/",
                "models": [
                    {
                        "id": "players.PlayerAttributes",
                        "name": "Player attributess",
                        "url": "/admin/players/playerattributes/",
                        "url_add": "/admin/players/playerattributes/add/",
                        "objects": [
                            {
                                "id": str(match.pk),
                                "name": str(match),
                                "url": f"/admin/players/playerattributes/{match.pk}",
                            }
                        ],
                    }
                ],
            }
        ]
    }
    assert data["counts"] == {"apps": 1, "models": 1, "objects": 1}
    assert not data["errors"]


def test_counts(client_super_admin):
    """Verify that counts are correct: each value is the total number of results for that
    entity"""
    TeamFactory(name="Manchester United")
    TeamFactory(name="Manchester City")
    PlayerFactory(name="Manuel Almunia")
    StadiumFactory(name="Manchester Arena")

    response = request_search(client_super_admin, query="man")
    data = response.json()

    assert response.status_code == 200
    assert data["counts"] == {"apps": 3, "models": 3, "objects": 4}
    assert not data["errors"]


@pytest.mark.parametrize("method", ["model_char_fields", "admin_search_fields"])
def test_limit(client_super_admin, method):
    """Verify that a maximum of 5 objects, for each model is returned"""
    for i in range(8):
        GroupFactory(name=f"Internal {i}")

    response = request_search(
        client_super_admin, query="internal", site_search_method=method
    )

    data = response.json()

    assert response.status_code == 200
    assert len(data["results"]["apps"][0]["models"][0]["objects"]) == 5
    assert data["counts"] == {"apps": 1, "models": 1, "objects": 5}
    assert not data["errors"]


@override_settings(DEBUG=True)
def test_errors_on(client_super_admin):
    """Verify errors that occur on-or-below the "model" level are skipped, and - if DEBUG=True - included
    in the response"""
    team = TeamFactory(name="Arsenal")
    StadiumFactory(name="Arsenal Stadium")

    def error_if_stadium(_, app_label, model_dict):
        """Fails for the Stadium model, default otherwise"""
        if model_dict["object_name"] == "Stadium":
            raise Exception("A test error occurred")
        else:
            return apps.get_model(app_label, model_dict["object_name"])

    with patch.object(AdminSiteSearchView, "get_model_class") as get_model_class:
        get_model_class.side_effect = error_if_stadium

        response = request_search(client_super_admin, query="Arsenal")
        data = response.json()

    assert response.status_code == 200
    assert len(data.keys()) == 3
    assert data["results"] == {
        "apps": [
            {
                "id": "teams",
                "name": "Teams",
                "url": "/admin/teams/",
                "models": [
                    {
                        "id": "teams.Team",
                        "name": "Teams",
                        "url": "/admin/teams/team/",
                        "url_add": "/admin/teams/team/add/",
                        "objects": [
                            {
                                "id": str(team.pk),
                                "name": str(team),
                                "url": f"/admin/teams/team/{team.pk}",
                            }
                        ],
                    }
                ],
            }
        ]
    }
    assert data["counts"] == {"apps": 1, "models": 1, "objects": 1}
    assert len(data["errors"]) == 1
    assert data["errors"][0] == {
        "error": "Exception('A test error occurred')",
        "error_message": "A test error occurred",
        "app": "stadiums",
        "model": "Stadium",
    }


@override_settings(DEBUG=False)
def test_errors_off(client_super_admin):
    """Verify errors are skipped, but not included in the response, if DEBUG=False"""
    with patch.object(AdminSiteSearchView, "get_model_class") as get_model_class:
        # everything will fail
        get_model_class.side_effect = Exception

        response = request_search(client_super_admin, query="not good")
        data = response.json()

    assert response.status_code == 200
    assert data["results"] == {"apps": []}
    assert data["counts"] == {"apps": 0, "models": 0, "objects": 0}
    assert not data["errors"]
