# django-admin-site-search

A global/site search modal for the Django admin.

<img src="https://raw.githubusercontent.com/ahmedaljawahiry/django-admin-site-search/main/images/demo.gif" width="100%" alt="Preview/demo GIF" />

## Features

- 🎩 Works out-of-the-box, with minimal config.
- 🔎 Search performed on:
  - App labels.
  - Model labels and field attributes.
  - CharField values (with `__icontains`).
    - Subclasses also included: `SlugField`, `URLField`, etc.
- 🔒 Built-in auth: users can only search apps and models that they have permission to view.
- ⚡ Results appear on-type, with throttling/debouncing to avoid excessive requests.
- 🎹 Keyboard navigation (cmd+k, up/down, enter).
- ✨ Responsive, and supports dark/light mode.
  - Django's built-in CSS vars are used to match your admin theme.

## Requirements

- Python 3.8 - 3.11.
- Django 3.2 - 4.1.

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

Methods in `AdminSiteSearchView` can be extended to add custom logic.

```python 
def match_app(self, query: str, name: str) -> bool:
    """DEFAULT: case-insensitive match the app name"""
    ...

def match_model(
    self, query: str, name: str, object_name: str, fields: List[Field]
) -> bool:
    """DEFAULT: case-insensitive match the model and field attributes"""
    ...

def match_objects(
    self, query: str, model_class: Model, model_fields: List[Field]
) -> QuerySet:
    """DEFAULT: Returns the QuerySet after performing an OR filter across all Char fields in the model."""
    ...

def filter_field(self, query: str, field: Field) -> Optional[Q]:
    """DEFAULT: Returns a Q 'icontains' filter for Char fields, otherwise None"""
    ...
```

### Example

**Add `TextField` results to search.**

```python
class MyAdminSite(AdminSiteSearchView, admin.AdminSite):
    ...  
  
    def filter_field(self, query: str, field: Field) -> Optional[Q]:
        """Extends super() to add TextField support to site search"""
        if isinstance(field, TextField):
            return Q(**{f"{field.name}__icontains": query})
        return super().filter_field(query, field)
```

Note that this isn't done by default for performance reasons: `__icontains` on a 
large number of text entries is inefficient.


## Screenshots
<img src="https://raw.githubusercontent.com/ahmedaljawahiry/django-admin-site-search/main/images/desktop-light-open.png" width="100%" alt="Desktop, light theme, modal open" />
<p>
  <img src="https://raw.githubusercontent.com/ahmedaljawahiry/django-admin-site-search/main/images/mobile-light-closed.png" width="45%" alt="Mobile, light theme, modal closed" />
  <img src="https://raw.githubusercontent.com/ahmedaljawahiry/django-admin-site-search/main/images/mobile-dark-open.png" width="45%" alt="Mobile, dark theme, modal open" /> 
</p>
