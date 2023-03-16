"""Test factories for the stadiums app"""
import factory
from factory.fuzzy import BaseFuzzyAttribute

from dev.football.stadiums.models import Stadium, Pitch


class StadiumFactory(factory.django.DjangoModelFactory):
    """Factory for the Stadium model"""

    name = factory.fuzzy.FuzzyText()
    key = factory.fuzzy.FuzzyText()
    capacity = factory.fuzzy.FuzzyInteger(low=1000, high=100000)

    class Meta:
        model = Stadium


class PitchFactory(factory.django.DjangoModelFactory):
    """Factory for the Pitch model"""

    stadium = factory.SubFactory(StadiumFactory)
    surface_type = "GRASS"
    width = factory.fuzzy.FuzzyInteger(low=6000, high=7000)
    length = factory.fuzzy.FuzzyInteger(low=10000, high=11000)

    class Meta:
        model = Pitch
