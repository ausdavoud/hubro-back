from typing import Any

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from ...models.common import RippleTask
from ...models.people import CustomUser, Instructor, Player, SimulationClass, Team
from ...models.rd import DynamicRD
from ...views.services.ripple_tasks import create_dynamic_rd_ripple_task
from ..data_fixtures import dynamic_rd, players, simulation_classes, superusers, teams, users


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

        # RD Products
        self.start_research_for_rd_items(dynamic_rd)

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

    def start_research_for_rd_items(self, dynamic_rd):
        for dynamic_rd_dict in dynamic_rd:
            player_email = dynamic_rd_dict["player_email"]
            category = dynamic_rd_dict["category"]
            order = dynamic_rd_dict["order"]
            started_at = dynamic_rd_dict["started_at"]
            time_spent_developing = dynamic_rd_dict["time_spent_developing"]
            alias = dynamic_rd_dict.get("alias", "")
            icon_link = dynamic_rd_dict.get("icon_link", "")

            player = Player.objects.prefetch_related("rd").filter(user__email=player_email).first()
            if not player:
                self.stderr.write(f"No player with email {player_email} was found")
                continue

            try:
                dynamic_rd_object = player.rd.get(category=category, order=order)
                dynamic_rd_object.started_at = started_at
                dynamic_rd_object.time_spent_developing = time_spent_developing
                dynamic_rd_object.alias = alias
                dynamic_rd_object.icon_link = icon_link
                dynamic_rd_object.save()
                ripple_task = create_dynamic_rd_ripple_task(
                    player=player,
                    run_at_quarter=started_at + 1,
                    type=RippleTask.TaskTypes.INCREMENT_RD_DEV_TIME,
                    dynamic_rd_object=dynamic_rd_object,
                )
                self.stdout.write(f"Player {player_email} started research for {category} | column {order}")
            except DynamicRD.DoesNotExist:
                self.stderr.write(
                    f"No Dynamic R&D item with category {category} and order {order} was found for user {player.user.email}."
                    "Created a new one."
                )
