"""Enums for the players app"""

from enum import Enum

from django.utils.translation import gettext_lazy as _


class PlayerPosition(Enum):
    """Football player positions, on a pitch"""

    GK = _("Goal keeper")
    LB = _("Left back")
    CB = _("Centre back")
    RB = _("Right back")
    DM = _("Defensive midfield")
    CM = _("Central midfield")
    AM = _("Attacking midfield")
    LW = _("Left winger")
    RW = _("Right winger")
    ST = _("Striker")
