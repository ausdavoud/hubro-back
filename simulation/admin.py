from django.contrib import admin

from .models.common import RippleTask, StateVariable
from .models.finance import FinancialAccount
from .models.people import CustomUser, Instructor, Player, SimulationClass, Team
from .models.rd import DynamicRD, StaticRD

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Player)
admin.site.register(Instructor)
admin.site.register(SimulationClass)
admin.site.register(Team)
admin.site.register(FinancialAccount)
admin.site.register(StaticRD)
admin.site.register(DynamicRD)
admin.site.register(RippleTask)
admin.site.register(StateVariable)
