from typing import List, Optional

from django.apps import apps
from django.db.models import CharField, Field, Model, Q, QuerySet, TextField
from django.http import JsonResponse
from django.urls import path


class AdminSiteSearchView:
    """Adds a search/ view, to the admin site"""

    def get_urls(self):
        """Extends super()'s urls, to include search/"""
        urlpatterns = super().get_urls()

        search = path("search/", self.admin_view(self.search), name="search")
        # avoid append(), to keep the "catch_all_view" last
        urlpatterns.insert(0, search)

        return urlpatterns

    def search(self, request):
        """Returns a JsonResponse containing results from matching the "q" query parameter to
        application names, model names, and all instance CharFields. Only apps/models that the
        user has permission to view are searched."""
        query = request.GET.get("q", "").lower()

        results = {"apps": []}
        counts = {"apps": 0, "models": 0, "objects": 0}

        if not query:
            # missing query, so return empty results
            return JsonResponse({"results": results, "counts": counts})

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
                can_view = model["perms"]["view"]
                can_add = model["perms"]["add"]

                if not can_view:
                    # user has no permission to view this model, so skip
                    continue

                model_class = model.get(  # model class added to dict in django 4.x
                    "model", apps.get_model(app["app_label"], model["object_name"])
                )
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

            # we've matched some models or objects, or the app name
            if app_result["models"] or self.match_app(query, app["name"]):
                results["apps"].append(app_result)
                counts["apps"] += 1

        return JsonResponse({"results": results, "counts": counts})

    def match_app(self, query: str, name: str) -> bool:
        """Case-insensitive match the app name"""
        return query.lower() in name.lower()

    def match_model(
        self, query: str, name: str, object_name: str, fields: List[Field]
    ) -> bool:
        """Case-insensitive match the model and field names"""
        _query = query.lower()
        if _query in name.lower() or _query in object_name.lower():
            # return early if we match a name
            return True
        for field in fields:
            verbose_name = getattr(field, "verbose_name", "")
            help_text = getattr(field, "help_text", "")
            if _query in field.name or _query in verbose_name or _query in help_text:
                # return early if we match any field name
                return True
        return False

    def match_objects(
        self, query: str, model_class: Model, model_fields: List[Field]
    ) -> QuerySet:
        """Returns the QuerySet after performing an OR filter across all fields
        in the model"""
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
        """Returns a Q 'icontains' filter for Char & Text fields, otherwise None"""
        if isinstance(field, CharField) or isinstance(field, TextField):
            return Q(**{f"{field.name}__icontains": query})
