from django.contrib import admin, messages
from django.utils.translation import ngettext

from common.models import RippleTask
from people.models import CustomUser
from people.views.services import get_player_or_404
from rd.models import DynamicRD, StaticRD


class StaticRDAdmin(admin.ModelAdmin):
    list_display = ["id", "category", "order", "title", "type"]


class DynamicRDAdmin(admin.ModelAdmin):
    actions = ["make_ripple_task"]
    list_display = [
        "id",
        "player",
        "category",
        "order",
        "title",
        "type",
        "started_at",
        "development_duration",
        "time_spent_developing",
    ]

    @admin.action(description="Add ripple task only for R&D-Upgrade items")
    def make_ripple_task(self, request, dynamic_rd_objects: list[DynamicRD]):
        user: CustomUser = request.user
        player = get_player_or_404(user)
        # BUG
        # This action method uses the current quarter of the logged-in admin user
        # who is running the action. A better version would sort the dynamic_rd_objects
        # based on their players, then for each set of dynamic objects related to
        # a user, SELECT player along with its prefetched state variables and
        # use the player's current quarter as run_at_quarter field
        current_quarter = player.state_variables.quarter

        ripple_tasks = []
        for dynamic_rd_object in dynamic_rd_objects:
            # BUG
            # This action does not check for existing ripple tasks.
            # So you might create duplicates
            json_body = {"dynamic_rd_id": dynamic_rd_object.pk}
            ripple_task = RippleTask(
                player=player,
                run_at_quarter=current_quarter + 1,
                type=RippleTask.TaskTypes.INCREMENT_RD_DEV_TIME,
                json_body=json_body,
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


admin.site.register(StaticRD, StaticRDAdmin)
admin.site.register(DynamicRD, DynamicRDAdmin)
