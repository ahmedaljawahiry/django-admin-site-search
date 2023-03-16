from django.contrib import admin

from dev.football.core.admin import BaseAdmin
from dev.football.players.models import Player, PlayerAttributes, PlayerContract


@admin.register(Player)
class PlayerAdmin(BaseAdmin):
    """Admin for the Player model"""

    pass


@admin.register(PlayerAttributes)
class PlayerAttributes(BaseAdmin):
    """Admin for the PlayerAttributes model"""

    pass


@admin.register(PlayerContract)
class PlayerContractAdmin(BaseAdmin):
    """Admin for the PlayerContract model"""

    pass
