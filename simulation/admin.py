from django.contrib import admin

from .models.finance import FinancialAccount
from .models.people import CustomUser, Instructor, Player, SimulationClass, Team
from .models.simulation import RnDProduct, RnDStatic, RnDUpgrade

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Player)
admin.site.register(Instructor)
admin.site.register(SimulationClass)
admin.site.register(Team)
admin.site.register(FinancialAccount)
admin.site.register(RnDStatic)
admin.site.register(RnDProduct)
admin.site.register(RnDUpgrade)
