from django.contrib import admin, messages
from django.db.models import F
from django.utils.translation import ngettext

from .models.common import RippleTask, StateVariable
from .models.finance import FinancialAccount
from .models.people import CustomUser, Instructor, Player, SimulationClass, Team
from .models.rd import DynamicRD, StaticRD
from .views.services.common import get_player_or_404


class DynamicRDAdmin(admin.ModelAdmin):
    actions = ["make_ripple_task"]

    @admin.action(description="Add ripple task only for R&D-Upgrade items")
    def make_ripple_task(self, request, dynamic_rd_objects):
        user: CustomUser = request.user
        player = get_player_or_404(user)
        current_quarter = player.state_variables.quarter

        ripple_tasks = []
        for dynamic_rd_object in dynamic_rd_objects:
            ripple_task = RippleTask(
                player=player,
                run_at_quarter=current_quarter,
                type=RippleTask.TaskTypes.INCREMENT_RD_DEV_TIME,
                rd_object=dynamic_rd_object,
            )
            ripple_tasks.append(ripple_task)

        ripple_tasks_count = len(ripple_tasks)
        RippleTask.objects.bulk_create(ripple_tasks)
        self.message_user(
            request,
            ngettext(
                "%d ripple task was created",
                "%d ripple tasks were created",
                ripple_tasks_count,
            )
            % ripple_tasks_count,
            messages.SUCCESS,
        )


class RippleTaskAdmin(admin.ModelAdmin):
    actions = ["increment_run_at_quarter"]

    @admin.action(description="Increment run_at_quarter by 1")
    def increment_run_at_quarter(self, request, ripple_tasks):
        update = ripple_tasks.update(run_at_quarter=F("run_at_quarter") + 1)
        self.message_user(
            request,
            ngettext(
                "Incremented the 'run_at_quarter' for %d ripple task",
                "Incremented the 'run_at_quarter' for %d ripple tasks",
                update,
            )
            % update,
            messages.SUCCESS,
        )


# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Player)
admin.site.register(Instructor)
admin.site.register(SimulationClass)
admin.site.register(Team)
admin.site.register(FinancialAccount)
admin.site.register(StaticRD)
admin.site.register(DynamicRD, DynamicRDAdmin)
admin.site.register(RippleTask, RippleTaskAdmin)
admin.site.register(StateVariable)
