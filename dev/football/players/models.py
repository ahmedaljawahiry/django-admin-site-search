"""Models for the players app"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from dev.football.core.models import BaseModel
from dev.football.players.enums import PlayerPosition


class Player(BaseModel):
    """Model representing a Football Player, e.g. Bukayo Saka"""

    name = models.CharField(max_length=120, help_text=_("The full name of the player"))
    key = models.SlugField(
        max_length=120,
        help_text=_("Unique key, used in URLs and code references"),
        unique=True,
    )

    def __str__(self):
        """Returns the Player's name"""
        return self.name


class PlayerAttributes(BaseModel):
    """Model representing a set of attributes for a Football Player"""

    player = models.OneToOneField(
        Player,
        primary_key=True,
        on_delete=models.CASCADE,
        help_text=_("The player whose attributes these are"),
    )
    position = models.CharField(
        max_length=2,
        choices=[(p.name, p.value) for p in PlayerPosition],
        help_text=_("The player's primary position"),
    )
    nationality = models.CharField(
        max_length=64, help_text=_("The player's current nationality")
    )
    age = models.PositiveSmallIntegerField(help_text=_("The current age of the player"))
    score_defence = models.PositiveSmallIntegerField(
        help_text=_("The player's defensive score, out of 100"),
        default=50,
        validators=[MaxValueValidator(100), MinValueValidator(1)],
    )
    score_midfield = models.PositiveSmallIntegerField(
        help_text=_("The player's midfield score, out of 100"),
        default=50,
        validators=[MaxValueValidator(100), MinValueValidator(1)],
    )
    score_offence = models.PositiveSmallIntegerField(
        help_text=_("The player's attacking score, out of 100"),
        default=50,
        validators=[MaxValueValidator(100), MinValueValidator(1)],
    )


class PlayerContract(BaseModel):
    """Model representing a contract signed by a player"""

    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, help_text=_("The player signing the contract")
    )
    team = models.ForeignKey(
        "teams.Team",
        on_delete=models.CASCADE,
        help_text=_("The team signing the contract"),
    )
    valid_from = models.DateField(
        help_text=_("The date from which the contract is valid")
    )
    duration = models.PositiveSmallIntegerField(
        help_text=_("The length of the contract, in years")
    )
    terms = models.TextField(help_text=_("The agreed terms in the contract"))
