import sys
from typing import List, Optional

from django.apps import apps
from django.conf import settings
from django.contrib.admin import ModelAdmin
from django.db.models import CharField, Field, Model, Q, QuerySet
from django.http import HttpRequest, JsonResponse
from django.urls import path

if sys.version_info >= (3, 8):
    from typing import Literal

    SiteSearchMethodType = Literal["model_char_fields", "admin_search_fields"]
else:
    SiteSearchMethodType = str


class AdminSiteSearchView:
    """Adds a search/ view, to the admin site"""

    site_search_path = "search/"
    site_search_method: SiteSearchMethodType = "model_char_fields"

    def get_urls(self):
        """Extends super()'s urls, to include search/"""
        urlpatterns = super().get_urls()

        search = path(
            self.site_search_path, self.admin_view(self.search), name="site-search"
        )
        # avoid append() so that "catch_all_view" is last
        urlpatterns.insert(0, search)

        return urlpatterns

    def search(self, request: HttpRequest) -> JsonResponse:
        """Returns a JsonResponse containing results from matching the "q" query parameter to
        application names, model names, and all instance CharFields. Only apps/models that the
        user has permission to view are searched.

        :param request: The HTTPRequest object."""
        query = request.GET.get("q", "")

        results = {"apps": []}
        counts = {"apps": 0, "models": 0, "objects": 0}
        errors = []

        if not query:
            # missing query, so return empty results
            return JsonResponse(
                {"results": results, "counts": counts, "errors": errors}
            )

        # same app list used to create the admin page for a user
        app_list = self.get_app_list(request)

        for app in app_list:
            app_result = {
                "id": app["app_label"],
                "name": app["name"],
                "url": app["app_url"] if app["has_module_perms"] else None,
                "models": [],
            }

            for model in app["models"]:
                try:
                    can_view = model["perms"]["view"]
                    can_add = model["perms"]["add"]

                    if not can_view:
                        # user has no permission to view this model, so skip
                        continue

                    model_class = self.get_model_class(request, app["app_label"], model)
                    if not model_class:
                        # unable to retrieve model class, so skip
                        continue

                    fields = model_class._meta.get_fields()
                    objects = self.match_objects(request, query, model_class, fields)

                    # haven't matched any objects, or model names, so skip
                    if not objects and not self.match_model(
                        request, query, model["name"], model["object_name"], fields
                    ):
                        continue

                    model_result = {
                        "id": f"{app['app_label']}.{model['object_name']}",
                        "name": model["name"],
                        "url": model["admin_url"],
                        "url_add": model["add_url"] if can_add else None,
                        "objects": [],
                    }

                    for obj in objects:
                        object_result = {
                            "id": str(obj.pk),
                            "name": str(obj),
                            "url": f"{model['admin_url']}{obj.pk}",
                        }
                        model_result["objects"].append(object_result)
                        counts["objects"] += 1

                    app_result["models"].append(model_result)
                    counts["models"] += 1
                except Exception as ex:
                    # except/skip to avoid unexpected issues with one model preventing any results
                    # from being returned - log the error client-side instead (not in production)
                    if settings.DEBUG:
                        errors.append(
                            {
                                "error": repr(ex),
                                "error_message": str(ex),
                                "app": app["app_label"],
                                "model": model["object_name"],
                            }
                        )
                    continue

            # we've matched some models or objects, or the app name
            if app_result["models"] or self.match_app(request, query, app["name"]):
                results["apps"].append(app_result)
                counts["apps"] += 1

        return JsonResponse({"results": results, "counts": counts, "errors": errors})

    def match_app(self, request: HttpRequest, query: str, name: str) -> bool:
        """Case-insensitive match the app name.

        :param request: The HTTPRequest object.
        :param query: The search query string.
        :param name: The name of the app."""
        return query.lower() in name.lower()

    def match_model(
        self,
        request: HttpRequest,
        query: str,
        name: str,
        object_name: str,
        fields: List[Field],
    ) -> bool:
        """Case-insensitive match the model and field attributes.

        :param request: The HTTPRequest object.
        :param query: The search query string.
        :param name: The (verbose) name of the model.
        :param object_name: The name of the model class.
        :param fields: A list of the model's fields."""
        _query = query.lower()
        if _query in name.lower() or _query in object_name.lower():
            # return early if we match a name
            return True
        for field in fields:
            verbose_name = getattr(field, "verbose_name", "")
            help_text = getattr(field, "help_text", "")
            if _query in field.name or _query in verbose_name or _query in help_text:
                # return early if we match any field attr
                return True
        return False

    def match_objects(
        self,
        request: HttpRequest,
        query: str,
        model_class: Model,
        model_fields: List[Field],
    ) -> QuerySet:
        """Returns the QuerySet[:5] after performing a search, as per the site_search_method:

        - model_char_fields: OR filter across all Char fields in the model.
        - admin_search_fields: delegates search to the model's corresponding admin search_fields.

        :param request: The HTTPRequest object.
        :param query: The search query string.
        :param model_class: The model class.
        :param model_fields: A list of the model's fields.
        """
        results = model_class.objects.none()
        model_admin = self._registry.get(model_class)
        queryset = self.get_model_queryset(request, model_class, model_admin)

        if self.site_search_method == "model_char_fields":
            filters = Q()

            for field in model_fields:
                filter_ = self.filter_field(request, query, field)
                if filter_:
                    filters |= filter_

            if filters:
                results = queryset.filter(filters)
        elif self.site_search_method == "admin_search_fields":
            if model_admin and model_admin.search_fields:
                results, may_have_duplicates = model_admin.get_search_results(
                    request=request, queryset=queryset, search_term=query
                )

                if may_have_duplicates:
                    # can happen if search_fields contains a many-to-many relation
                    results = results.distinct()

        return results[:5]

    def filter_field(
        self, request: HttpRequest, query: str, field: Field
    ) -> Optional[Q]:
        """Returns a Q 'icontains' filter for Char fields, otherwise None.

        Note: this method is only invoked if model_char_fields is the site_search_method.

        :param request: The HTTPRequest object.
        :param query: The search query string.
        :param field: The model field to (optionally) filter on.
        """
        _query = query.lower()
        if isinstance(field, CharField):
            return Q(**{f"{field.name}__icontains": _query})

    def get_model_queryset(
        self,
        request: HttpRequest,
        model_class: Model,
        model_admin: Optional[ModelAdmin],
    ) -> QuerySet:
        """Returns the model class' .objects.all() queryset.

        :param request: The HTTPRequest object.
        :param model_class: The model class.
        :param model_admin: The model admin, which is non-None for all registered models.
        """
        return model_class.objects.all()

    def get_model_class(
        self, request: HttpRequest, app_label: str, model_dict: dict
    ) -> Optional[Model]:
        """Retrieves the model class from the dict created by admin.AdminSite, which (by default) contains:

        - "model": the class instance (only available in Django 4.x),
        - "name": capitalised verbose_name_plural,
        - "object_name": the class name,
        - "perms": dict of user permissions for this model,
        - other (e.g. url) fields.

        :param request: The HTTPRequest object.
        :param app_label: The label/name of the model's app.
        :param model_dict: A dict containing model information."""
        model_class = model_dict.get("model")
        if not model_class:
            # model_dict["model"] only available in django 4.x
            model_class = apps.get_model(app_label, model_dict["object_name"])
        return model_class
