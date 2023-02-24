from django.db.models import CharField, Q
from django.http import JsonResponse
from django.urls import path


class AdminSiteSearchMixin:
    """Mixin that adds a search/ view, to the admin site"""

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

        if query:
            app_list = self.get_app_list(request)

            for app in app_list:
                app_id = app["app_label"]
                app_name = app["name"]

                app_result = {
                    "id": app_id,
                    "name": app_name,
                    "url": app["app_url"] if app["has_module_perms"] else None,
                    "models": [],
                }

                for model in app["models"]:
                    model_obj_name = model["object_name"]
                    model_name = model["name"]
                    model_class = model["model"]
                    model_admin_url = model["admin_url"]
                    model_perms = model["perms"]

                    objects = []
                    if model_perms["view"]:
                        filters = Q()
                        for field in model_class._meta.get_fields():
                            if isinstance(field, CharField):
                                filters |= Q(**{f"{field.name}__icontains": query})

                        if filters:
                            objects = model_class.objects.filter(filters)[:5]

                        if (
                            query in model_name.lower()
                            or query in model_obj_name.lower()
                            or objects
                        ):
                            can_add = model_perms["add"] and not model["view_only"]

                            model_result = {
                                "id": f"{app_id}.{model_obj_name}",
                                "name": model_name,
                                "url": model_admin_url,
                                "url_add": model["add_url"] if can_add else None,
                                "objects": [],
                            }

                            for obj in objects:
                                object_result = {
                                    "id": obj.id,
                                    "name": str(obj),
                                    "url": f"{model_admin_url}{obj.id}",
                                }
                                model_result["objects"].append(object_result)
                                counts["objects"] += 1

                            app_result["models"].append(model_result)
                            counts["models"] += 1

                if query in app_name.lower() or app_result["models"]:
                    results["apps"].append(app_result)
                    counts["apps"] += 1

        return JsonResponse({"results": results, "counts": counts})
