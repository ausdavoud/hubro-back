from django.contrib import admin, messages
from django.db.models import F
from django.utils.translation import ngettext

from common.models import RippleTask, StateVariable


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


admin.site.register(RippleTask, RippleTaskAdmin)
admin.site.register(StateVariable)
