from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


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
    class UserRole(models.TextChoices):
        PLAYER = "PL", "Player"
        INSTRUCTOR = "IN", "Instructor"

    username = None
    email = models.EmailField(max_length=100, unique=True)
    role = models.CharField(
        max_length=2, choices=UserRole.choices, blank=True, null=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        app_label = "simulation"

    def save(self, *args, **kwargs):
        if self.role == "PL":
            player = Player(user=self)
            player.save()
        elif self.role == "IN":
            instructor = Instructor(user=self)
            instructor.save()
        super(CustomUser, self).save(*args, **kwargs)


class Instructor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="instructor"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email


class SimulationClass(models.Model):
    name = models.CharField(max_length=50)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "SimulationClasses"

    def __str__(self):
        return f"{self.name} supervised by {self.instructor}"


class Team(models.Model):
    name = models.CharField(max_length=50)
    sim_class = models.ForeignKey(SimulationClass, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="player"
    )
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, blank=True, null=True, related_name="players"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email
