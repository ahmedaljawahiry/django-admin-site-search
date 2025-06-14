"""Pytest fixtures and functions, for Playwright tests that run with a browser"""

import re

import pytest
from playwright.sync_api import Locator, Page, expect

from dev.football.core.management.commands.testdata import PASSWORD, USERNAME


@pytest.fixture
def page_admin(page) -> Page:
    """Returns an authenticated instance of the admin page, running locally on port 8000.

    Note: using live_server (https://pytest-django.readthedocs.io/en/latest/helpers.html#live-server)
    leads to DJANGO_ALLOW_ASYNC_UNSAFE-related errors. For now, the server needs to be up-and-running
    before accessing this fixture.
    """
    page.goto("http://localhost:8000/admin/")

    re_username = re.compile("username", re.IGNORECASE)
    page.get_by_role("textbox", name=re_username).type(USERNAME)

    re_password = re.compile("password", re.IGNORECASE)
    page.get_by_role("textbox", name=re_password).type(PASSWORD)

    page.get_by_role("button", name=re.compile("log in", re.IGNORECASE)).click()

    # verify that login worked
    re_logout = re.compile("Log out", re.IGNORECASE)
    expect(page.get_by_role("button", name=re_logout)).to_be_visible()

    return page


def search_button(page: Page) -> Locator:
    """Returns the search button, which opens the modal"""
    re_search_site = re.compile("search site", re.IGNORECASE)
    return page.get_by_role("button", name=re_search_site)


def search_box(page: Page) -> Locator:
    """Returns the search box, visible in the open modal"""
    re_search_site_input = re.compile("search site input", re.IGNORECASE)
    return page.get_by_role("textbox", name=re_search_site_input)


def expect_modal_open(page: Page):
    """Verifies that the modal is open by checking that the search input is visible"""
    expect(search_box(page)).to_be_visible()


def expect_modal_closed(page: Page):
    """Verifies that the modal is closed by checking that the search input is not visible"""
    expect(search_box(page)).not_to_be_visible()


def open_modal(page: Page, with_keyboard: bool = False):
    """Opens the modal, with the button or keyboard, then waits for it to appear"""
    if with_keyboard:
        page.keyboard.press("Control+k")
    else:
        search_button(page).click()

    expect_modal_open(page)
