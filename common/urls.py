from django.urls import path

from common.views import views

urlpatterns = [
    path(
        "finish_quarter/", views.FinishQuarter.as_view(), name="finish_quarter"
    ),
    path(
        "create_new_simulation/",
        views.CreateNewSimulation.as_view(),
        name="create_new_simulation",
    ),
    path(
        "join_simulation_queue/",
        views.JoinSimulationQueue.as_view(),
        name="join_simulation_queue",
    ),
    path(
        "get_simulation_queue/<str:simulation_code>",
        views.GetSimulationQueue.as_view(),
        name="get_simulation_queue",
    ),
    path(
        "start_new_simulation/",
        views.StartNewSimulation.as_view(),
        name="start_new_simulation",
    ),
    path(
        "set_company_info/",
        views.SetCompanyInfo.as_view(),
        name="set_company_info",
    ),
    path(
        "get_state_variables/",
        views.StateVariableView.as_view(),
        name="get_state_variables",
    ),
    path(
        "get_simulation_class_info/",
        views.GetSimulationInfo.as_view(),
        name="get_simulation_view",
    ),
]
