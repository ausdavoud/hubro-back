from django.contrib import admin

from people.models import CustomUser, Instructor, Player, SimulationClass, Team

admin.site.register(CustomUser)
admin.site.register(Player)
admin.site.register(Instructor)
admin.site.register(SimulationClass)
admin.site.register(Team)
