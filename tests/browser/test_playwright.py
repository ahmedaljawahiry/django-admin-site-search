"""Playwright tests verifying basic browser behaviour. These rely on the data created
by the "testdata" management command."""

from playwright.sync_api import expect

from tests.browser.conftest import (
    expect_modal_closed,
    expect_modal_open,
    open_modal,
    search_box,
    search_button,
)


def test_modal_admin_pages(page_admin):
    """Verify that the modal is available on all admin pages, not just the index"""

    # use a loop instead of parameterised test, to avoid loading & logging-in every time
    for path in ["auth/", "auth/user/", "auth/user/add/", "auth/user/1/change/"]:
        page_admin.goto(f"http://localhost:8000/admin/{path}")
        # button visible => html is there
        expect(search_button(page_admin)).to_be_visible()
        expect_modal_closed(page_admin)
        # open/close => JS is there
        page_admin.keyboard.press("Control+k")
        expect_modal_open(page_admin)


def test_modal_other_pages(page_admin):
    """Verify that the modal is not available on non-admin pages"""

    # use a loop instead of parameterised test, to avoid loading & logging-in every time
    for path in ["", "admin/logout/", "auth/user/add/", "auth/user/1/change/"]:
        page_admin.goto(f"http://localhost:8000/{path}")
        expect(search_button(page_admin)).not_to_be_visible()
        expect_modal_closed(page_admin)
        page_admin.keyboard.press("Control+k")
        expect_modal_closed(page_admin)


def test_modal_click(page_admin):
    """Verify that the search button is visible, and displays the modal on click.

    Note: really awkward to click away from the modal, with locators, to verify that it
    closes (skip for now).
    """
    # modal closed by default
    expect_modal_closed(page_admin)

    # modal/search button is visible and clickable
    button = search_button(page_admin)
    expect(search_button(page_admin)).to_be_visible()
    button.click()

    expect_modal_open(page_admin)


def test_modal_keyboard(page_admin):
    """Verify that the modal can be toggled via keyboard shortcuts.

    Note: use Control (instead of CMD), since the CI runner won't be Apple."""
    # modal closed by default
    expect_modal_closed(page_admin)

    # modal open after ctrl+k
    page_admin.keyboard.press("Control+k")
    expect_modal_open(page_admin)

    # modal closed after esc
    page_admin.keyboard.press("Escape")
    expect_modal_closed(page_admin)


def test_results_display(page_admin):
    """Verify that search results are displayed on type"""
    open_modal(page_admin)
    expect(page_admin.get_by_text("Enter 2 or more characters...")).to_be_visible()

    search_box(page_admin).type("playwright")

    expect(
        page_admin.get_by_text("Showing 2 apps, 2 models, and 3 objects")
    ).to_be_visible()
    expect(page_admin.get_by_text("Enter 2 or more characters...")).not_to_be_visible()

    for result in [
        "Authentication and Authorization - app",
        "Users - model",
        "playwright",
        "Teams - app",
        "Teams - model",
        "Playwright United FC",
        "Playwright City FC",
    ]:
        expect(page_admin.get_by_role("link", name=result, exact=True)).to_be_visible()


def test_results_none(page_admin):
    """Verify the "no results" message is displayed if there are no results"""
    open_modal(page_admin)
    expect(page_admin.get_by_text("Enter 2 or more characters...")).to_be_visible()

    search_box(page_admin).type("zero matches")

    expect(page_admin.get_by_text('No results for "zero matches"')).to_be_visible()
    expect(page_admin.get_by_text("Enter 2 or more characters...")).not_to_be_visible()


def test_results_keyboard(page_admin):
    """Verify the search result keyboard navigation:
    - up/down to cycle through results,
    - "text" key moves focus back to input,
    - enter triggers link."""
    open_modal(page_admin, with_keyboard=True)
    search_box(page_admin).type("playwri")

    expect(
        page_admin.get_by_text("Showing 2 apps, 2 models, and 3 objects")
    ).to_be_visible()

    page_admin.keyboard.press("ArrowDown")
    page_admin.keyboard.press("ArrowDown")

    # first key won't be inputted, but focused moved back input
    page_admin.keyboard.press("g")
    search_box(page_admin).type("ght")

    expect(
        page_admin.get_by_text("Showing 2 apps, 2 models, and 3 objects")
    ).to_be_visible()

    # go down, then navigate to the "playwright" user
    page_admin.keyboard.press("ArrowDown")
    page_admin.keyboard.press("ArrowDown")
    page_admin.keyboard.press("ArrowDown")
    page_admin.keyboard.press("Enter")

    # should be on the instance change page
    expect(page_admin.get_by_text("Change user", exact=True)).to_be_visible()
    expect(page_admin.get_by_label("Username:")).to_have_value("playwright")


def test_search_uri_encoded(page_admin):
    """Verify that search terms containing encoded URI components are supported"""
    open_modal(page_admin)
    search_box(page_admin).type("#,&")

    expect(
        page_admin.get_by_text("Showing 1 app, 1 model, and 1 object")
    ).to_be_visible()
    expect(page_admin.get_by_role("link", name="###,&&&", exact=True)).to_be_visible()
