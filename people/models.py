from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models import CheckConstraint, Q
from django.db.utils import IntegrityError


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError("The Email must be set")
        if not password:
            raise ValueError("Password is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()

        if user.role == CustomUser.UserRoles.PLAYER:
            try:
                player = Player.objects.create(user=user)
                from common.views.views import create_new_simulation_data

                create_new_simulation_data(player=player)
            except IntegrityError:
                print(f"A `Player` instance is already assigned to {user.email}")

        elif user.role == CustomUser.UserRoles.INSTRUCTOR:
            try:
                instructor = Instructor.objects.create(user=user)
            except IntegrityError:
                print(f"An `Instructor` instance is already assigned to {user.email}")

        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_active", True)

        if kwargs.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if kwargs.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **kwargs)


class CustomUser(AbstractUser):
    class UserRoles(models.TextChoices):
        PLAYER = "PL", "Player"
        INSTRUCTOR = "IN", "Instructor"

    username = None
    email = models.EmailField(max_length=100, unique=True)
    role = models.CharField(max_length=2, choices=UserRoles.choices, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        app_label = "people"

    def __str__(self):
        return self.email


class Instructor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="instructor")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email


class SimulationClass(models.Model):
    name = models.CharField(max_length=50)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, null=True)
    is_single_player = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        if
        is_single_player is True (it's single mode)
        =>
        instructor can be null
        p => q is equivalent to ~p | q
        """

        constraints = [
            CheckConstraint(
                check=~Q(is_single_player=True) | Q(instructor=None),
                name="check_instructor_not_null_if_team_mode",
            )
        ]
        verbose_name_plural = "SimulationClasses"

    def __str__(self):
        return self.name


class Team(models.Model):
    class TeamType(models.TextChoices):
        PLAYER = "PL", "Player"
        BOT = "BO", "Bot"

    name = models.CharField(max_length=50)
    simulation_class = models.ForeignKey(SimulationClass, on_delete=models.SET_NULL, null=True)
    team_type = models.CharField(max_length=2, choices=TeamType.choices, default=TeamType.PLAYER)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="player")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name="players")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email
