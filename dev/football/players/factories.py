"""Test factories for the players app"""
import factory
from factory.fuzzy import BaseFuzzyAttribute

from dev.football.players.models import Player, PlayerAttributes


class PlayerFactory(factory.django.DjangoModelFactory):
    """Factory for the Player model"""

    name = factory.fuzzy.FuzzyText()
    key = factory.fuzzy.FuzzyText()

    class Meta:
        model = Player


class PlayerAttributesFactory(factory.django.DjangoModelFactory):
    """Factory for the Player model"""

    player = factory.SubFactory(PlayerFactory)
    position = "CM"
    age = factory.fuzzy.FuzzyInteger(low=1, high=50)
    score_defence = factory.fuzzy.FuzzyInteger(low=1, high=100)
    score_midfield = factory.fuzzy.FuzzyInteger(low=1, high=100)
    score_offence = factory.fuzzy.FuzzyInteger(low=1, high=100)

    class Meta:
        model = PlayerAttributes
