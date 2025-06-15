"""Custom configuration for the admin"""

from django.contrib import admin
from django.contrib.admin.apps import AdminConfig

from admin_site_search.views import AdminSiteSearchView


class CustomAdminSite(AdminSiteSearchView, admin.AdminSite):
    """Adds the AdminSiteSearchView to the default AdminSite"""

    pass


class CustomAdminConfig(AdminConfig):
    """Custom admin config, with a custom default_site"""

    default_site = "dev.admin.CustomAdminSite"
