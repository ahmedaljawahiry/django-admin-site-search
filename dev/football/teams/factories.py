"""Test factories for the teams app"""
import factory
from factory.fuzzy import BaseFuzzyAttribute

from dev.football.stadiums.factories import StadiumFactory
from dev.football.teams.models import Team, Squad


class FuzzyURL(factory.fuzzy.BaseFuzzyAttribute):
    """Fuzzy class for URLs"""

    def fuzz(self):
        """Returns a random .com url"""
        return f"https://{factory.fuzzy.FuzzyText().fuzz()}.com".lower()


class TeamFactory(factory.django.DjangoModelFactory):
    """Factory for the Team model"""

    name = factory.fuzzy.FuzzyText()
    key = factory.fuzzy.FuzzyText()
    type = "CLUB"
    website = FuzzyURL()
    stadium = factory.SubFactory(StadiumFactory)

    class Meta:
        model = Team


class SquadFactory(factory.django.DjangoModelFactory):
    """Factory for the Squad model"""

    team = factory.SubFactory(TeamFactory)
    type = "SENIOR_MEN"

    class Meta:
        model = Squad
