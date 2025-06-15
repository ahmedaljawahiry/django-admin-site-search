"""Management command for creating test data. This should be called before running
Playwright tests, but can also be useful for local dev."""

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import IntegrityError

from dev.football.players.factories import PlayerAttributesFactory, PlayerFactory
from dev.football.stadiums.factories import PitchFactory, StadiumFactory
from dev.football.teams.factories import SquadFactory, TeamFactory
from dev.football.teams.models import Team

USERNAME = "playwright"
PASSWORD = "playwright-e2e-testing"

TEAM_1 = "Playwright United FC"
TEAM_2 = "Playwright City FC"
TEAM_3 = "###,&&&"


class Command(BaseCommand):
    """Creates test data, if it doesn't exist already"""

    help = "Create test data"

    def handle(self, *args, **options):
        # create the "fixed" test user, unless it already exists
        self.stdout.write("Creating constant test user...")
        try:
            User.objects.create_superuser(username=USERNAME, password=PASSWORD)
            self.stdout.write(self.style.SUCCESS(f'Created user "{USERNAME}"'))
        except IntegrityError:
            self.stdout.write(self.style.WARNING(f'User "{USERNAME}" already exists'))

        # create the "fixed" test teams, unless they already exist
        self.stdout.write("Creating constant test teams...")
        for name in [TEAM_1, TEAM_2, TEAM_3]:
            team_exists = Team.objects.filter(name=name).exists()
            if not team_exists:
                TeamFactory(name=name)
                self.stdout.write(self.style.SUCCESS(f'Created team "{name}"'))
            else:
                self.stdout.write(self.style.WARNING(f'Team "{name}" already exists'))

        # create a bunch of random data (not strictly necessary, but why not)
        self.stdout.write("Creating random data...")
        for factory in [
            PlayerFactory,
            PlayerAttributesFactory,
            StadiumFactory,
            PitchFactory,
            TeamFactory,
            SquadFactory,
        ]:
            obj = factory()
            self.stdout.write(self.style.SUCCESS(f'Created "{obj}"'))
