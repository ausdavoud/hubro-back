from django.contrib import admin

from people.models import (
    CustomUser,
    Instructor,
    Player,
    SimulationClass,
    SimulationClassQueue,
    Team,
)


class SimulationClassAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "instructor"]


class TeamAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "simulation_class"]


class PlayerAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "team"]


class SimulationClassQueueAdmin(admin.ModelAdmin):
    list_display = ("id", "player", "simulation_class")


admin.site.register(CustomUser)
admin.site.register(Instructor)
admin.site.register(SimulationClass, SimulationClassAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(SimulationClassQueue, SimulationClassQueueAdmin)
