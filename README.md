# django-admin-site-search

A global/site search modal for the Django admin.

<img src="https://raw.githubusercontent.com/ahmedaljawahiry/django-admin-site-search/main/images/demo.gif" width="100%" alt="Preview/demo GIF" />

## Features

- 🎩 Works out-of-the-box, with minimal config.
- 🔎 Search performed on:
  - App labels.
  - Model labels and fields.
  - Object Char and Text fields (with `__icontains`).
- 🔒 Built-in auth: users can only search apps and models that they have permission to view.
- ⚡ Results appear on-type, with throttling/debouncing to avoid excessive requests.
- 🎹 Keyboard navigation (cmd+k, up/down, enter).
- ✨ Responsive, and supports dark/light mode.
  - Uses Django's built-in CSS vars to match your admin theme.

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

## Notes

- Along with styles, the `admin_site_search/head.html` loads [Alpine JS](https://alpinejs.dev). 
  - This is the only external dependency.
- Search is implemented with basic `icontains`/`in` logic. Full-text search is out-of-scope.
- Methods in `AdminSiteSearchView`; such as `match_model`, `match_objects`, etc. can be extended to add any custom logic. 
- The placement of `modal.html` and `button.html` are not strict, though the former would ideally be in a top-level
position. 
  - Django 4.x exposes `{% block header %}` - this is preferable to `footer`.

## Screenshots
<img src="https://raw.githubusercontent.com/ahmedaljawahiry/django-admin-site-search/main/images/desktop-light-open.png" width="100%" alt="Desktop, light theme, modal open" />
<p>
  <img src="https://raw.githubusercontent.com/ahmedaljawahiry/django-admin-site-search/main/images/mobile-light-closed.png" width="45%" alt="Mobile, light theme, modal closed" />
  <img src="https://raw.githubusercontent.com/ahmedaljawahiry/django-admin-site-search/main/images/mobile-dark-open.png" width="45%" alt="Mobile, dark theme, modal open" /> 
</p>
