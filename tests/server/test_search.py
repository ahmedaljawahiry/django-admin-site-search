"""Tests verifying functionality for searching/matching apps, models and objects"""

import pytest

from admin_site_search.views import AdminSiteSearchView
from dev.football.players.admin import PlayerAdmin
from dev.football.players.factories import PlayerFactory
from dev.football.teams.admin import SquadAdmin, TeamAdmin
from dev.football.teams.factories import SquadFactory, TeamFactory
from tests import request_search


@pytest.mark.parametrize("method", ["model_char_fields", "admin_search_fields"])
@pytest.mark.parametrize(
    "query, results_expected",
    # take care to not match model names or fields
    [
        ("authentication and a", ["Authentication and Authorization"]),
        ("AUTHORIZATion", ["Authentication and Authorization"]),
        ("accounting", []),
    ],
)
def test_apps(client_super_admin, method, query, results_expected):
    """Verify 'contains' and case-insensitive matches are applied to the app name"""
    response = request_search(
        client_super_admin, query=query, site_search_method=method
    )

    data = response.json()
    results_actual = [r["name"] for r in data["results"]["apps"]]

    assert response.status_code == 200
    assert len(results_actual) == len(results_expected)
    assert not set(results_actual).difference(set(results_expected))


@pytest.mark.parametrize("method", ["model_char_fields", "admin_search_fields"])
@pytest.mark.parametrize(
    "query, results_expected",
    [
        ("stadium", ["Stadiums", "Pitchs", "Teams"]),
        ("STADIum", ["Stadiums", "Pitchs", "Teams"]),
        ("playerattributes", ["Player attributess", "Players"]),
        ("PlayerAttr", ["Player attributess", "Players"]),
        ("contract", ["Player contracts", "Players", "Teams"]),
        ("contracted", []),
        ("website", ["Teams"]),
        ("key", ["Players", "Stadiums", "Teams"]),
        ("WIDTH", ["Pitchs"]),
        ("playing surface", ["Pitchs"]),
    ],
)
def test_models(client_super_admin, method, query, results_expected):
    """Verify 'contains' and case-insensitive matches are applied to:
    - Model name,
    - Model object name,
    - Field names,
    - Field help text."""
    response = request_search(
        client_super_admin, query=query, site_search_method=method
    )

    data = response.json()
    results_actual = []

    for app in data["results"]["apps"]:
        for model in app["models"]:
            results_actual.append(model["name"])

    assert response.status_code == 200
    assert len(results_actual) == len(results_expected)
    assert not set(results_actual).difference(set(results_expected))


@pytest.mark.parametrize(
    "method, query, results_expected",
    [
        ("model_char_fields", "obj-one", ["obj-one"]),
        ("model_char_fields", "obj-two", ["obj-TWO"]),
        ("model_char_fields", "-ONE", ["obj-one"]),
        ("model_char_fields", "one two", []),
        ("model_char_fields", "slug-key", ["obj-one", "obj-TWO"]),
        ("model_char_fields", "two.com", ["obj-TWO"]),
        ("model_char_fields", "Text", []),  # TextField not matched
        ("admin_search_fields", "obj-one", ["obj-one"]),
        ("admin_search_fields", "obj-two", ["obj-TWO"]),
        ("admin_search_fields", "-ONE", ["obj-one"]),
        ("admin_search_fields", "one two", []),
        ("admin_search_fields", "slug-key", []),  # "=" prefix, so exact match only
        ("admin_search_fields", "slug-key-obj-one", ["obj-one"]),
        ("admin_search_fields", "https", []),  # not in admin search_fields
        ("admin_search_fields", "Text", ["obj-one", "obj-TWO"]),  # TextField is matched
        ("invalid", "obj", []),
    ],
)
def test_objects(client_super_admin, method, query, results_expected):
    """
    Verify that objects are queried as per the site_search_method:

    - model_char_fields: only CharFields are matched, with icontains. Note: contains acts like icontains
    in SQLite, so we're not currently asserting on the latter.
    - admin_search_fields: search functionality in the model's corresponding admin class is invoked
    (https://docs.djangoproject.com/en/5.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.search_fields).
    - invalid: no objects returned.
    """

    for i, n in enumerate(["obj-one", "obj-TWO"], start=999):
        TeamFactory(
            id=i,
            name=f"{n}",
            key=f"slug-key-{n}",
            website=f"https://url.{n}.com",
            description=f"Text {n}",
        )

    response = request_search(
        client_super_admin, query=query, site_search_method=method
    )

    data = response.json()
    results_actual = []

    for app in data["results"]["apps"]:
        for model in app["models"]:
            for obj in model["objects"]:
                results_actual.append(obj["name"])

    assert TeamAdmin.search_fields == ("name", "description", "=key")
    assert response.status_code == 200
    assert len(results_actual) == len(results_expected)
    assert not set(results_actual).difference(set(results_expected))


def test_objects_admin_search_fields_none(client_super_admin):
    """Verify that objects are not matched if the corresponding admin has no
    "search_fields" set"""
    PlayerFactory(name="Test")

    response = request_search(
        client_super_admin, query="Test", site_search_method="admin_search_fields"
    )

    data = response.json()
    results_actual = [r["name"] for r in data["results"]["apps"]]

    assert not PlayerAdmin.search_fields
    assert response.status_code == 200
    assert len(results_actual) == 0


def test_objects_admin_search_fields_relations(client_super_admin):
    """Verify that relations are searched, if defined in the corresponding admin search_fields"""
    team = TeamFactory(name="team-1")
    squad_1 = SquadFactory(team=team)
    squad_2 = SquadFactory(team=team)

    # other team with other squad
    team_other = TeamFactory(name="team-2")
    SquadFactory(team=team_other)

    response = request_search(
        client_super_admin, query="team-1", site_search_method="admin_search_fields"
    )

    data = response.json()
    results = {}

    for app in data["results"]["apps"]:
        for model in app["models"]:
            results[model["name"]] = [o["id"] for o in model["objects"]]

    assert SquadAdmin.search_fields == ("team__name", "players__name")
    assert len(results["Squads"]) == 2
    assert str(squad_1.id) in results["Squads"]
    assert str(squad_2.id) in results["Squads"]
    assert len(results["Teams"]) == 1
    assert str(team.id) in results["Teams"]


def test_objects_admin_search_fields_distinct(client_super_admin):
    """Verify that duplicates are removed, if they arise from relation many-to-many searches"""
    squad = SquadFactory()
    player_1 = PlayerFactory(name="John Doe")
    player_2 = PlayerFactory(name="Doe John")
    squad.players.add(player_1, player_2)

    response = request_search(
        client_super_admin, query="john", site_search_method="admin_search_fields"
    )

    data = response.json()
    results = data["results"]["apps"][0]["models"][0]["objects"]

    assert SquadAdmin.search_fields == ("team__name", "players__name")
    assert len(results) == 1
    assert results[0]["id"] == str(squad.id)


def test_objects_method_default():
    """Verify that, by default, site_search_method=model_char_fields.

    This is set to avoid breaking changes in behaviour."""
    assert AdminSiteSearchView.site_search_method == "model_char_fields"
