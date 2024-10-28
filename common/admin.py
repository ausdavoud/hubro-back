from django.contrib import admin, messages
from django.db.models import F
from django.utils.translation import ngettext

from common.models import DecisionPool, RippleTask, StateVariable


class DecisionPoolAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "player",
        "made_at_quarter",
        "endpoint",
        "json_body",
    ]


class StateVariableAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "player",
        "esg_index",
        "fixed_interest",
        "quarter",
        "simulation_duration",
        "max_loan_repayment_duration",
    ]


class RippleTaskAdmin(admin.ModelAdmin):
    list_display = ["id", "player", "run_at_quarter", "type", "dynamic_rd_object"]
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


admin.site.register(DecisionPool, DecisionPoolAdmin)
admin.site.register(StateVariable, StateVariableAdmin)
admin.site.register(RippleTask, RippleTaskAdmin)
