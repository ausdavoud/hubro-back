from typing import Any

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from simulation.models.simulation import RnDProduct, RnDStatic, RnDUpgrade

from ...models.people import CustomUser, Instructor, Player, SimulationClass, Team
from ..static_objects import RnD_products, RnD_upgrades, players, simulation_classes, superusers, teams, users


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

        # RnD Products
        self.create_rnd_products(RnD_products)

        # RnD Upgrades
        self.create_rnd_upgrades(RnD_upgrades)

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

    def create_rnd_products(self, RnD_products):
        for rnd_product_dict in RnD_products:
            email = rnd_product_dict["player_email"]
            column_num = rnd_product_dict["static"]["column_num"]
            product_key = rnd_product_dict["static"]["product_key"]
            rnd_product_kwargs = rnd_product_dict["kwargs"]

            player = Player.objects.filter(user__email=email).first()
            static = RnDStatic.objects.filter(product_key=product_key)[column_num - 1]
            rnd_product_obj = RnDProduct.objects.filter(player=player, static=static).first()

            if rnd_product_obj:
                self.stderr.write(
                    f"The same R&d Product with alias {rnd_product_obj.alias} already exists for {player.user.email}"
                )
                continue

            rnd_product_obj = RnDProduct.objects.create(player=player, static=static, **rnd_product_kwargs)
            self.stdout.write(f"Created R&D Product {static.title} for {player.user.email}")

    def create_rnd_upgrades(self, RnD_upgrades):
        for rnd_upgrade_dict in RnD_upgrades:
            email = rnd_upgrade_dict["player_email"]
            column_num = rnd_upgrade_dict["static"]["column_num"]
            product_key = rnd_upgrade_dict["static"]["product_key"]
            updated_product_alias = rnd_upgrade_dict["updated_product_alias"]
            rnd_upgrade_kwargs = rnd_upgrade_dict["kwargs"]

            player = Player.objects.filter(user__email=email).first()
            static = RnDStatic.objects.filter(product_key=product_key)[column_num - 1]
            updated_product_obj = RnDProduct.objects.filter(alias=updated_product_alias, player=player).first()
            rnd_upgrade_obj = RnDUpgrade.objects.filter(player=player, static=static).first()

            if rnd_upgrade_obj:
                self.stderr.write(f"The same R&d Upgrade already exists for {player.user.email}")
                continue

            rnd_upgrade_obj = RnDUpgrade.objects.create(
                player=player, static=static, updated_product=updated_product_obj, **rnd_upgrade_kwargs
            )
            self.stdout.write(f"Created R&D Upgrade for {updated_product_obj.alias} for {player.user.email}")
