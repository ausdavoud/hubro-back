from django.contrib import admin

from .models.people import CustomUser, Instructor, SimulationClass, Team, Player

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Player)
admin.site.register(Instructor)
admin.site.register(SimulationClass)
admin.site.register(Team)