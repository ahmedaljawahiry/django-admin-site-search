"""Custom configuration for the admin"""
from django.contrib import admin
from django.contrib.admin.apps import AdminConfig

from search.views import AdminSiteSearchMixin


class CustomAdminSite(AdminSiteSearchMixin, admin.AdminSite):
    """Adds the AdminSiteSearchMixin to the default AdminSite"""

    pass


class CustomAdminConfig(AdminConfig):
    """Custom admin config, with a custom default_site"""

    default_site = "dev.admin.CustomAdminSite"
