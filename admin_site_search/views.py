from typing import List, Optional

from django.apps import apps
from django.conf import settings
from django.db.models import CharField, Field, Model, Q, QuerySet
from django.http import JsonResponse
from django.urls import path


class AdminSiteSearchView:
    """Adds a search/ view, to the admin site"""

    site_search_path = "search/"

    def get_urls(self):
        """Extends super()'s urls, to include search/"""
        urlpatterns = super().get_urls()

        search = path(
            self.site_search_path, self.admin_view(self.search), name="site-search"
        )
        # avoid append() so that "catch_all_view" is last
        urlpatterns.insert(0, search)

        return urlpatterns

    def search(self, request):
        """Returns a JsonResponse containing results from matching the "q" query parameter to
        application names, model names, and all instance CharFields. Only apps/models that the
        user has permission to view are searched."""
        query = request.GET.get("q", "").lower()

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

                    model_class = self.get_model_class(app["app_label"], model)
                    if not model_class:
                        # unable to retrieve model class, so skip
                        continue

                    fields = model_class._meta.get_fields()
                    objects = self.match_objects(query, model_class, fields)

                    # haven't matched any objects, or model names, so skip
                    if not objects and not self.match_model(
                        query, model["name"], model["object_name"], fields
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
            if app_result["models"] or self.match_app(query, app["name"]):
                results["apps"].append(app_result)
                counts["apps"] += 1

        return JsonResponse({"results": results, "counts": counts, "errors": errors})

    def match_app(self, query: str, name: str) -> bool:
        """Case-insensitive match the app name"""
        return query.lower() in name.lower()

    def match_model(
        self, query: str, name: str, object_name: str, fields: List[Field]
    ) -> bool:
        """Case-insensitive match the model and field attributes"""
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
        self, query: str, model_class: Model, model_fields: List[Field]
    ) -> QuerySet:
        """Returns the QuerySet[:5] after performing an OR filter across all Char fields in the model."""
        filters = Q()

        for field in model_fields:
            filter_ = self.filter_field(query, field)
            if filter_:
                filters |= filter_

        if filters:
            results = model_class.objects.filter(filters)[:5]
        else:
            results = model_class.objects.none()

        return results

    def filter_field(self, query: str, field: Field) -> Optional[Q]:
        """Returns a Q 'icontains' filter for Char fields, otherwise None"""
        if isinstance(field, CharField):
            return Q(**{f"{field.name}__icontains": query})

    def get_model_class(self, app_label: str, model_dict: dict) -> Optional[Model]:
        """Retrieve the model class from the dict created by admin.AdminSite, which (by default) contains:
        - "model": the class instance (only available in Django 4.x),
        - "name": capitalised verbose_name_plural,
        - "object_name": the class name,
        - "perms": dict of user permissions for this model,
        - other (e.g. url) fields."""
        model_class = model_dict.get("model")
        if not model_class:
            # model_dict["model"] only available in django 4.x
            model_class = apps.get_model(app_label, model_dict["object_name"])
        return model_class
