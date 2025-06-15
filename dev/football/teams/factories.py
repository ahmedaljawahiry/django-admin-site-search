"""Test factories for the teams app"""

from factory import SubFactory, django, fuzzy

from dev.football.stadiums.factories import StadiumFactory
from dev.football.teams.models import Squad, Team


class FuzzyURL(fuzzy.BaseFuzzyAttribute):
    """Fuzzy class for URLs"""

    def fuzz(self):
        """Returns a random .com url"""
        return f"https://{fuzzy.FuzzyText().fuzz()}.com".lower()


class TeamFactory(django.DjangoModelFactory):
    """Factory for the Team model"""

    name = fuzzy.FuzzyText()
    key = fuzzy.FuzzyText()
    type = "CLUB"
    website = FuzzyURL()
    motto = fuzzy.FuzzyText()
    stadium = SubFactory(StadiumFactory)

    class Meta:
        model = Team


class SquadFactory(django.DjangoModelFactory):
    """Factory for the Squad model"""

    team = SubFactory(TeamFactory)
    type = "SENIOR_MEN"

    class Meta:
        model = Squad
