# django-admin-site-search

[![Test](https://github.com/ahmedaljawahiry/django-admin-site-search/actions/workflows/test.yaml/badge.svg)](https://github.com/ahmedaljawahiry/django-admin-site-search/actions/workflows/test.yaml)
[![Lint](https://github.com/ahmedaljawahiry/django-admin-site-search/actions/workflows/lint.yaml/badge.svg)](https://github.com/ahmedaljawahiry/django-admin-site-search/actions/workflows/lint.yaml)
[![PyPI](https://github.com/ahmedaljawahiry/django-admin-site-search/actions/workflows/pypi.yaml/badge.svg)](https://github.com/ahmedaljawahiry/django-admin-site-search/actions/workflows/pypi.yaml)
[![Coverage Python](https://img.shields.io/badge/coverage%20(.py)-100%25-brightgreen.svg)](https://github.com/ahmedaljawahiry/django-admin-site-search/actions/workflows/test.yaml)
[![Coverage Javascript](https://img.shields.io/badge/coverage%20(.js)-TBD-green.svg)](https://github.com/ahmedaljawahiry/django-admin-site-search/actions/workflows/test.yaml)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Pre-Commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logoColor=white)](https://github.com/ahmedaljawahiry/django-admin-site-search/blob/main/.pre-commit-config.yaml)
[![PyPI version](https://img.shields.io/pypi/v/django-admin-site-search.svg)](https://pypi.org/project/django-admin-site-search/)
[![Downloads](https://static.pepy.tech/badge/django-admin-site-search)](https://pepy.tech/project/django-admin-site-search)
[![PyPI license](https://img.shields.io/pypi/l/django-admin-site-search.svg)](https://github.com/ahmedaljawahiry/django-admin-site-search/blob/main/LICENSE)

A global/site search modal for the Django admin.

<img src="https://raw.githubusercontent.com/ahmedaljawahiry/django-admin-site-search/main/images/demo.gif" width="100%" alt="Preview/demo GIF" />

## Features

- 🎩 Works out-of-the-box, with minimal config.
- 🔎 Search performed on:
  - App labels.
  - Model labels and field attributes.
  - Model instances, with two options for a search method:
    1. `model_char_fields` (_default_): All `CharField` (and subclass) values, with `__icontains`.
    2. `admin_search_fields`: Invoke each ModelAdmin's
[get_search_results(...)](https://docs.djangoproject.com/en/5.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.get_search_results) method.
- 🔒 Built-in auth: users can only search apps and models that they have permission to view.
- ⚡ Results appear on-type, with throttling/debouncing to avoid excessive requests.
- 🎹 Keyboard navigation (cmd+k, up/down, enter).
- ✨ Responsive, and supports dark/light mode.
  - Django's built-in CSS vars are used to match your admin theme.

## Requirements

- Python 3.7 - 3.12.
- Django 3.2 - 5.1.

## Setup

### 1. Install

1. Install with your package manager, e.g. `pip install django-admin-site-search`.
2. Add `admin_site_search` to your `INSTALLED_APPS` setting.

### 2. Add View

1. If you haven't already, [override/extend the default AdminSite](https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#overriding-the-default-admin-site).
2. Add the `AdminSiteSearchView` to your AdminSite:

```python
from django.contrib import admin
from admin_site_search.views import AdminSiteSearchView

class MyAdminSite(AdminSiteSearchView, admin.AdminSite):
    ...
```


### 3. Add Templates

1. If you haven't already, create `admin/base_site.html` in your `templates/` directory.
   - Note: if your `templates/` directory is inside of an app, then that app must appear in `INSTALLED_APPS` _before_ your custom admin app.
2. Include the `admin_site_search` templates:
```html
{% extends "admin/base_site.html" %}

{% block extrahead %}
    {% include 'admin_site_search/head.html' %}
    {{ block.super }}
{% endblock %}

{% block footer %}
    {{ block.super }}
    {% include 'admin_site_search/modal.html' %}
{% endblock %}

{% block usertools %}
    {% include 'admin_site_search/button.html' %}
    {{ block.super }}
{% endblock %}
```

#### Notes

- Along with styles, `admin_site_search/head.html` loads [Alpine JS](https://alpinejs.dev). 
  - This is bundled into `/static/`, to avoid external dependencies.
- The placement of `modal.html` and `button.html` are not strict, though the former would ideally be in a top-level
position. 
  - Django 4.x exposes `{% block header %}` - this is preferable to `footer`.

## Customisation

### Class attributes

```python
class MyAdminSite(AdminSiteSearchView, admin.AdminSite):
    
    # Sets the last part of the search route (`<admin_path>/search/`).
    site_search_path: str = "search/"
    # Set the search method/behaviour.
    site_search_method: Literal["model_char_fields", "admin_search_fields"] = "model_char_fields" 
```

### Methods

```python 
def match_app(
    self, request, query: str, name: str
) -> bool:
    """DEFAULT: case-insensitive match the app name"""

def match_model(
    self, request, query: str, name: str, object_name: str, fields: List[Field]
) -> bool:
    """DEFAULT: case-insensitive match the model and field attributes"""

def match_objects(
    self, request, query: str, model_class: Model, model_fields: List[Field]
) -> QuerySet:
    """DEFAULT: Returns the QuerySet after performing an OR filter across all Char fields in the model."""

def filter_field(
    self, request, query: str, field: Field
) -> Optional[Q]:
    """DEFAULT: Returns a Q 'icontains' filter for Char fields, otherwise None
    
    Note: this method is only invoked if model_char_fields is the site_search_method."""

def get_model_queryset(
    self, request, model_class: Model, model_admin: Optional[ModelAdmin]
) -> QuerySet:
    """DEFAULT: Returns the model class' .objects.all() queryset."""

def get_model_class(
    self, request, app_label: str, model_dict: dict
) -> Optional[Model]:
    """DEFAULT: Retrieve the model class from the dict created by admin.AdminSite"""
```

#### Example

**Add `TextField` results to search.**

```python
from django.contrib import admin
from django.db.models import Q, Field, TextField
from admin_site_search.views import AdminSiteSearchView


class MyAdminSite(AdminSiteSearchView, admin.AdminSite):
    
    site_search_method: "model_char_fields"  
  
    def filter_field(self, request, query: str, field: Field) -> Optional[Q]:
        """Extends super() to add TextField support to site search"""
        if isinstance(field, TextField):
            return Q(**{f"{field.name}__icontains": query})
        return super().filter_field(query, field)
```

Note that this isn't done by default for performance reasons: `__icontains` on a 
large number of text entries is suboptimal.


## Screenshots
<img src="https://raw.githubusercontent.com/ahmedaljawahiry/django-admin-site-search/main/images/desktop-light-open.png" width="100%" alt="Desktop, light theme, modal open" />
<p>
  <img src="https://raw.githubusercontent.com/ahmedaljawahiry/django-admin-site-search/main/images/mobile-light-closed.png" width="45%" alt="Mobile, light theme, modal closed" />
  <img src="https://raw.githubusercontent.com/ahmedaljawahiry/django-admin-site-search/main/images/mobile-dark-open.png" width="45%" alt="Mobile, dark theme, modal open" /> 
</p>
