from django.test import Client
from django.urls import reverse


def request_search(client: Client, query: str = ""):
    """Returns the response after performing a GET request against the "admin:site-search"
    endpoint, with the given client and query"""
    url = f'{reverse("admin:site-search")}?q={query}'

    return client.get(url)
