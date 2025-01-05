from people.models import Team


def get_simulation_teams(team: Team) -> list[Team]:
    """
    Returns a list of teams that are in the same simulation with the given team.
    """
    return Team.objects.filter(simulation_class=team.simulation_class)
