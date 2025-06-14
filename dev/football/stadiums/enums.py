"""Enums for the stadiums app"""

from enum import Enum

from django.utils.translation import gettext_lazy as _


class PitchSurfaceType(Enum):
    """Types of surface for football pitch"""

    GRASS = _("Grass")
    HYBRID = _("Hybrid")
    ARTIFICIAL = _("Artificial")
