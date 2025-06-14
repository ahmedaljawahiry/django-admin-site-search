"""Test factories for core or built-in models"""

from django.contrib.auth.models import Group
from factory import django, fuzzy


class GroupFactory(django.DjangoModelFactory):
    """Factory for the built-in Group model"""

    name = fuzzy.FuzzyText()

    class Meta:
        model = Group
