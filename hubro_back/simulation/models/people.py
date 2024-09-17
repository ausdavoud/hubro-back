from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class CustomUser(AbstractUser):
    class UserRole(models.TextChoices):
        PLAYER = "PL", "Player"
        INSTRUCTOR = "IN", "Instructor"

    role = models.CharField(max_length=2, choices=UserRole.choices, blank=True, null=True)

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class SimulationClass(models.Model):
    name = models.CharField(max_length=50)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "SimulationClasses"

    def __str__(self):
        return f"{self.name} supervised by {self.Instructor}"


class Team(models.Model):
    name = models.CharField(max_length=50)
    sim_class = models.ForeignKey(SimulationClass, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
