"""Tests verifying templates are included in the admin site. I.e. ensure the extension
to admin/base_site.html is supported/working."""

import django
import pytest
from django.test import Client
from django.urls import reverse

# presence confirms that the package's templates have loaded correctly
ELEMENTS_CUSTOM = [
    '<script src="/static/admin_site_search/alpinejs/focus-3-12-0.min.js" defer>',
    '<script src="/static/admin_site_search/alpinejs/3-12-0.min.js" defer>',
    '<script src="/static/admin_site_search/search.js',
    "[x-cloak] { display: none !important;}",
    '<link rel="stylesheet" href="/static/admin_site_search/style.css">',
    '<template x-data x-if="$store.search.isOpen">',
    '<button id="search-site-button"',
]

# presence confirms that existing elements are still loaded, and not overridden
ELEMENT_HEADER = '<a href="/admin/">Django administration</a>'
if django.VERSION[0] >= 5 and django.VERSION[1] >= 1:
    ELEMENT_FOOTER = '<footer id="footer">'
else:
    ELEMENT_FOOTER = '<div id="footer">'
ELEMENT_USER_TOOL = '<div id="user-tools">'


def request_admin_content(
    client: Client,
    view_name: str = "index",
    query_str: str = "",
    method: str = "get",
    follow: bool = True,
) -> str:
    """Returns the response's content after GETing the admin site"""
    path = reverse(f"admin:{view_name}")
    response = getattr(client, method)(f"{path}?{query_str}", follow=follow)
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
    assert ELEMENT_FOOTER in content
    assert ELEMENT_USER_TOOL in content


def test_popup(client_super_admin):
    """Verify that the elements are not included in popups"""
    content = request_admin_content(client_super_admin, "auth_group_add", "_popup=1")

    for element in ELEMENTS_CUSTOM:
        assert element not in content

    assert ELEMENT_HEADER not in content
    assert ELEMENT_FOOTER in content
    assert ELEMENT_USER_TOOL not in content


def test_login(client_super_admin):
    """Verify that the elements are omitted from the login page"""
    client_super_admin.logout()
    content = request_admin_content(client_super_admin)

    for element in ELEMENTS_CUSTOM:
        assert element not in content

    assert ELEMENT_HEADER in content
    assert ELEMENT_FOOTER in content
    assert ELEMENT_USER_TOOL not in content


def test_logout(client_super_admin):
    """Verify that the elements are omitted from the logout page"""
    content = request_admin_content(
        client_super_admin, "logout", method="post", follow=False
    )

    for element in ELEMENTS_CUSTOM:
        assert element not in content

    assert ELEMENT_HEADER in content
    assert ELEMENT_FOOTER in content
    assert ELEMENT_USER_TOOL not in content
