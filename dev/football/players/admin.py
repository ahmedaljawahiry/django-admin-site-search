from django.contrib import admin

from dev.football.core.admin import BaseAdmin
from dev.football.players.models import Player, PlayerAttributes, PlayerContract


class PlayerAttributesInline(admin.TabularInline):
    """Inline admin for Player Attributes"""

    model = PlayerAttributes
    extra = 0


@admin.register(Player)
class PlayerAdmin(BaseAdmin):
    """Admin for the Player model"""

    inlines = (PlayerAttributesInline,)


@admin.register(PlayerContract)
class PlayerContractAdmin(BaseAdmin):
    """Admin for the PlayerContract model"""

    pass
