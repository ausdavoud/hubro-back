from django.contrib import admin, messages
from django.utils.translation import ngettext

from common.models import RippleTask
from common.views.services import get_db_record_select_prefetch_or_404
from people.models import CustomUser, Player
from rd.models import DynamicRD


class DynamicRDAdmin(admin.ModelAdmin):
    actions = ["make_ripple_task"]
    list_display = [
        "id",
        "team",
        "category",
        "order",
        "title",
        "type",
        "supplier",
        "development_duration",
        "time_spent_developing",
        "started_at",
        "is_completed",
    ]

    @admin.action(description="Add ripple task only for R&D-Upgrade items")
    def make_ripple_task(self, request, dynamic_rd_objects: list[DynamicRD]):
        user: CustomUser = request.user
        player = get_db_record_select_prefetch_or_404(Player, user=user)
        team = player.team
        # BUG
        # This action method uses the current quarter of the logged-in admin user
        # who is running the action. A better version would sort the dynamic_rd_objects
        # based on their players, then for each set of dynamic objects related to
        # a user, SELECT player along with its prefetched state variables and
        # use the player's current quarter as run_at_quarter field
        current_quarter = team.simulation_class.current_quarter

        ripple_tasks = []
        for dynamic_rd_object in dynamic_rd_objects:
            # BUG
            # This action does not check for existing ripple tasks.
            # So you might create duplicates
            json_body = {"dynamic_rd_id": dynamic_rd_object.pk}
            ripple_task = RippleTask(
                team=team,
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


admin.site.register(DynamicRD, DynamicRDAdmin)
