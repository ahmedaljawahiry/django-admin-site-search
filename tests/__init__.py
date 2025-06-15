from typing import Optional
from unittest.mock import patch

from django.test import Client
from django.urls import reverse

from admin_site_search.views import AdminSiteSearchView, SiteSearchMethodType


def request_search(
    client: Client,
    query: str = "",
    site_search_method: Optional[SiteSearchMethodType] = None,
):
    """Returns the response after performing a GET request against the "admin:site-search"
    endpoint, with the given client and query.

    If site_search_method is given, the value is set via patch.object(...)."""
    url = f"{reverse('admin:site-search')}?q={query}"

    if site_search_method is None:
        # by default, don't patch anything
        response = client.get(url)
    else:
        with patch.object(
            AdminSiteSearchView, "site_search_method", site_search_method
        ):
            response = client.get(url)

    return response
