"""Verify that the search path supports admin sites with custom URLs"""

import re

from django.test import Client, override_settings
from django.urls import reverse

from admin_site_search.views import AdminSiteSearchView


def request_script_element(client: Client):
    """Requests admin:index, then parses the content for the search.js script element. This should
    contain the necessary attributes to detect the admin URL."""
    response = client.get(reverse("admin:index"), follow=True)
    content = str(response.content)

    script_element = re.search(
        r'<script src="/static/admin_site_search/search.js.*</script>', content
    ).group(0)

    return script_element


@override_settings(ROOT_URLCONF="tests.server.test_url.urls_default")
def test_default(client_super_admin):
    """Verify the correct URL is set for default url conf"""
    element = request_script_element(client_super_admin)

    assert 'id="admin-site-search-script"' in element
    assert 'data-search-path="/admin/search/"' in element


@override_settings(ROOT_URLCONF="tests.server.test_url.urls_custom")
def test_custom(client_super_admin):
    """Verify the correct URL is set for a custom url conf"""
    element = request_script_element(client_super_admin)

    assert 'id="admin-site-search-script"' in element
    assert 'data-search-path="/custom/search/"' in element


@override_settings(ROOT_URLCONF="tests.server.test_url.urls_index")
def test_index(client_super_admin):
    """Verify the correct URL is set for a custom url conf, with the admin at the index"""
    element = request_script_element(client_super_admin)

    assert 'id="admin-site-search-script"' in element
    assert 'data-search-path="/search/"' in element


def test_path_attr():
    """Verify that the AdminSiteSearchView has a "site_search_path", which is used to generate
    the search route"""

    # basic assertions to avoid crazy patches - this is more of a sanity test to prevent API breakages
    assert hasattr(AdminSiteSearchView, "site_search_path")
    assert reverse("admin:site-search").endswith(AdminSiteSearchView.site_search_path)
