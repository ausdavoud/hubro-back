from typing import Any

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from ...models.people import CustomUser, Instructor, Player, SimulationClass, Team
from ..static_objects import players, simulation_classes, superusers, teams, users


class Command(BaseCommand):
    help = (
        "Add predefined Superusers, Users, Instructors, Teams, Players, "
        "non-static R&D Projects, non-static R&D Upgrades."
    )

    def handle(self, *args: Any, **options: Any) -> str | None:
        # Superusers
        self.cerate_super_users(superusers)

        # Users
        self.create_users(users)

        # Simulation Class
        self.create_simulation_classes(simulation_classes)

        # Teams:
        self.create_teams(teams)

        # Players
        self.assign_team_to_players(players)

    def cerate_super_users(self, superusers):
        for superuser_dict in superusers:
            try:
                superuser_obj = CustomUser.objects.create_superuser(**superuser_dict)
                self.stdout.write(f"Created superuser {superuser_obj.email} as {superuser_dict['role']}")
            except IntegrityError:
                self.stderr.write(f"Superuser {superuser_dict['email']} already exists")

    def create_users(self, users):
        for user_dict in users:
            try:
                user_obj = CustomUser.objects.create_user(**user_dict)
                self.stdout.write(f"Created user {user_obj.email} as {user_dict['role']} ")
            except IntegrityError:
                self.stderr.write(f"User {user_dict['email']} already exists")

    def create_simulation_classes(self, simulation_classes):
        for simulation_class_dict in simulation_classes:
            name = simulation_class_dict["name"]
            instructor_email = simulation_class_dict["instructor_email"]

            if SimulationClass.objects.filter(name=name).exists():
                self.stderr.write(f"Simulation class {name} already exists")
                continue

            instructor_obj = Instructor.objects.filter(user__email=instructor_email).first()

            if not instructor_obj:
                self.stderr.write(f"No instructor {instructor_email} for simulation class {name} was found")
                continue

            simulation_class_obj = SimulationClass.objects.create(name=name, instructor=instructor_obj)
            self.stdout.write(f"Simulation class {simulation_class_obj.name} was created")

    def create_teams(self, teams):
        for team_dict in teams:
            name = team_dict["name"]
            simulation_class_name = team_dict["simulation_class_name"]

            if Team.objects.filter(name=name).exists():
                self.stderr.write(f"Team {name} already exists")
                continue

            simulation_class_obj = SimulationClass.objects.filter(name=simulation_class_name).first()

            if not simulation_class_obj:
                self.stderr.write(f"No simulation class {simulation_class_name} for team {name} was found")
                continue

            team_obj = Team.objects.create(name=name, simulation_class=simulation_class_obj)
            self.stdout.write(f"Team {team_obj.name} was created")

    def assign_team_to_players(self, players):
        for player_dict in players:
            email = player_dict["player_email"]
            team_name = player_dict["team_name"]

            player_obj = Player.objects.filter(user__email=email).first()
            team_obj = Team.objects.filter(name=team_name).first()

            if Player.objects.filter(user__email=email, team=team_obj).exists():
                self.stderr.write(f"Player {email} already exists")
                continue
            if not player_obj:
                self.stderr.write(f"No player {email} was found")
                continue
            if not team_obj:
                self.stderr.write(f"No team {player_dict['team']} was found")
                continue

            player_obj.team = team_obj
            player_obj.save()
            self.stdout.write(f"Player {player_obj.user.email} was added to team {team_obj.name}")
