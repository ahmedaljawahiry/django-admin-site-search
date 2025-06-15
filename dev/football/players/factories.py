"""Test factories for the players app"""

from factory import SubFactory, django, fuzzy

from dev.football.players.models import Player, PlayerAttributes


class PlayerFactory(django.DjangoModelFactory):
    """Factory for the Player model"""

    name = fuzzy.FuzzyText()
    key = fuzzy.FuzzyText()

    class Meta:
        model = Player


class PlayerAttributesFactory(django.DjangoModelFactory):
    """Factory for the Player model"""

    player = SubFactory(PlayerFactory)
    position = "CM"
    age = fuzzy.FuzzyInteger(low=1, high=50)
    nationality = "British"
    score_defence = fuzzy.FuzzyInteger(low=1, high=100)
    score_midfield = fuzzy.FuzzyInteger(low=1, high=100)
    score_offence = fuzzy.FuzzyInteger(low=1, high=100)

    class Meta:
        model = PlayerAttributes
