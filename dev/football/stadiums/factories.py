"""Test factories for the stadiums app"""

from factory import SubFactory, django, fuzzy

from dev.football.stadiums.models import Pitch, Stadium


class StadiumFactory(django.DjangoModelFactory):
    """Factory for the Stadium model"""

    name = fuzzy.FuzzyText()
    key = fuzzy.FuzzyText()
    capacity = fuzzy.FuzzyInteger(low=1000, high=100000)

    class Meta:
        model = Stadium


class PitchFactory(django.DjangoModelFactory):
    """Factory for the Pitch model"""

    stadium = SubFactory(StadiumFactory)
    surface_type = "GRASS"
    width = fuzzy.FuzzyInteger(low=6000, high=7000)
    length = fuzzy.FuzzyInteger(low=10000, high=11000)

    class Meta:
        model = Pitch
