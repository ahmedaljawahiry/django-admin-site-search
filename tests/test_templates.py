"""Tests verifying templates are included in the admin site. I.e. ensure the extension
to admin/base_site.html is supported/working."""
import pytest
from django.test import Client
from django.urls import reverse

# presence confirms that the package's templates have loaded correctly
ELEMENTS_CUSTOM = [
    '<script src="https://cdn.jsdelivr.net/npm/@alpinejs/focus@3.11.1/dist/cdn.min.js" defer>',
    '<script src="https://cdn.jsdelivr.net/npm/alpinejs@3.11.1/dist/cdn.min.js" defer>',
    '<script src="/static/search/alpine.js">',
    "[x-cloak] { display: none !important;}",
    '<link rel="stylesheet" href="/static/search/style.css">',
    '<template x-data x-if="$store.search.isOpen">',
    '<button id="search-site-button"',
]

# presence confirms that the default header is still loaded, and not overridden
ELEMENT_HEADER = '<a href="/admin/">Django administration</a>'
# presence confirms that the default "user tools" are still loaded, and not overridden
ELEMENT_USER_TOOL = '<button type="submit">Log out</button>'


def request_admin_content(
    client: Client, view_name: str = "index", query_str: str = ""
) -> str:
    """Returns the response's content after GETing the admin site"""
    response = client.get(f'{reverse(f"admin:{view_name}")}?{query_str}', follow=True)
    return str(response.content)


@pytest.mark.parametrize(
    "view_name", ["index", "password_change", "auth_group_changelist"]
)
def test_authenticated(client_super_admin, view_name):
    """Verify that the elements are included in all authenticated views"""
    content = request_admin_content(client_super_admin, view_name)

    for element in ELEMENTS_CUSTOM:
        assert element in content

    assert ELEMENT_HEADER in content
    assert ELEMENT_USER_TOOL in content


def test_popup(client_super_admin):
    """Verify that the elements are not included in popups"""
    content = request_admin_content(client_super_admin, "auth_group_add", "_popup=1")

    for element in ELEMENTS_CUSTOM:
        assert element not in content

    assert ELEMENT_HEADER not in content
    assert ELEMENT_USER_TOOL not in content


def test_login(client_super_admin):
    """Verify that the elements are omitted from the login page"""
    client_super_admin.logout()
    content = request_admin_content(client_super_admin)

    for element in ELEMENTS_CUSTOM:
        assert element not in content

    assert ELEMENT_HEADER in content
    assert ELEMENT_USER_TOOL not in content


def test_logout(client_super_admin):
    """Verify that the elements are omitted from the logout page"""
    content = request_admin_content(client_super_admin, "logout")

    for element in ELEMENTS_CUSTOM:
        assert element not in content

    assert ELEMENT_HEADER in content
    assert ELEMENT_USER_TOOL not in content
