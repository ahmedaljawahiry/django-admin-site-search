"""Tests verifying functionality for searching/matching apps, models and objects"""
import pytest

from dev.football.teams.factories import TeamFactory
from tests import request_search


@pytest.mark.parametrize(
    "query, results_expected",
    # take care to not match model names or fields
    [
        ("authentication and a", ["Authentication and Authorization"]),
        ("AUTHORIZATion", ["Authentication and Authorization"]),
        ("accounting", []),
    ],
)
def test_apps(client_super_admin, query, results_expected):
    """Verify 'contains' and case-insensitive matches are applied to the app name"""
    response = request_search(client_super_admin, query=query)

    data = response.json()
    results_actual = [r["name"] for r in data["results"]["apps"]]

    assert response.status_code == 200
    assert len(results_actual) == len(results_expected)
    assert not set(results_actual).difference(set(results_expected))


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
def test_models(client_super_admin, query, results_expected):
    """Verify 'contains' and case-insensitive matches are applied to:
    - Model name,
    - Model object name,
    - Field names,
    - Field help text."""
    response = request_search(client_super_admin, query=query)

    data = response.json()
    results_actual = []

    for app in data["results"]["apps"]:
        for model in app["models"]:
            results_actual.append(model["name"])

    assert response.status_code == 200
    assert len(results_actual) == len(results_expected)
    assert not set(results_actual).difference(set(results_expected))


@pytest.mark.parametrize(
    "query, results_expected",
    [
        ("obj-one", ["obj-one"]),
        ("-ONE", ["obj-one"]),
        ("one two", []),
        ("slug-key", ["obj-one", "obj-two"]),
        ("two.com", ["obj-two"]),
        ("Text", []),
    ],
)
def test_objects(client_super_admin, query, results_expected):
    """Verify object CharFields are matched: 'contains' and case-insensitive. Other fields are not matched."""
    for i, n in enumerate(["obj-one", "obj-two"], start=999):
        TeamFactory(
            id=i,
            name=f"{n}",
            key=f"slug-key-{n}",
            website=f"https://url.{n}.com",
            description=f"Text {n}",
        )

    response = request_search(client_super_admin, query=query)

    data = response.json()
    results_actual = []

    for app in data["results"]["apps"]:
        for model in app["models"]:
            for obj in model["objects"]:
                results_actual.append(obj["name"])

    assert response.status_code == 200
    assert len(results_actual) == len(results_expected)
    assert not set(results_actual).difference(set(results_expected))
