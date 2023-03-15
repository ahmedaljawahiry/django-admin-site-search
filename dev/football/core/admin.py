from django.contrib import admin


class BaseAdmin(admin.ModelAdmin):
    """Adds base fields for all model admins"""

    readonly_fields = ("created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    ordering = ("-created_at",)
