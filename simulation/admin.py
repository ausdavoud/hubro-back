from django.contrib import admin

from .models.common import StateVariable

from .models.finance import FinancialAccount
from .models.people import CustomUser, Instructor, Player, SimulationClass, Team
from .models.rd import RDProduct, RDStatic, RDUpgrade

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Player)
admin.site.register(Instructor)
admin.site.register(SimulationClass)
admin.site.register(Team)
admin.site.register(FinancialAccount)
admin.site.register(RDStatic)
admin.site.register(RDProduct)
admin.site.register(RDUpgrade)
admin.site.register(StateVariable)
