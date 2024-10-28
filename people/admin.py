from django.contrib import admin

from people.models import CustomUser, Instructor, Player, SimulationClass, Team


class SimulationClassAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "instructor"]


class TeamAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "simulation_class"]


class PlayerAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "team"]


admin.site.register(CustomUser)
admin.site.register(Instructor)
admin.site.register(SimulationClass, SimulationClassAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Player, PlayerAdmin)
