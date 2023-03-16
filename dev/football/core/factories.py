"""Test factories for core or built-in models"""
from factory import fuzzy, django
from django.contrib.auth.models import Group


class GroupFactory(django.DjangoModelFactory):
    """Factory for the built-in Group model"""

    name = fuzzy.FuzzyText()

    class Meta:
        model = Group
