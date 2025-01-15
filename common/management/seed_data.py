from people.models import CustomUser
from rd.models import RDCategories

superusers = [
    {
        "email": "d@g.com",
        "password": "dddddddd",  # 8d
        "role": CustomUser.UserRoles.INSTRUCTOR,
    },
    {
        "email": "h@g.com",
        "password": "hhhhhhhh",  # 8h
        "role": CustomUser.UserRoles.PLAYER,
    },
    {
        "email": "s@g.com",
        "password": "ssssssss",  # 8s
        "role": CustomUser.UserRoles.PLAYER,
    },
    {
        "email": "dvin@gmail.com",
        "password": "11111111",
        "role": CustomUser.UserRoles.PLAYER,
    },
]


users = [
    {
        "email": "p@g.com",
        "password": "pppppppp",  # 8p
        "role": CustomUser.UserRoles.INSTRUCTOR,
    },
    {
        "email": "m@g.com",
        "password": "mmmmmmmm",  # 8m
        "role": CustomUser.UserRoles.PLAYER,
    },
    {
        "email": "a@g.com",
        "password": "aaaaaaaa",  # 8a
        "role": CustomUser.UserRoles.PLAYER,
    },
]

simulation_classes = [
    {"name": "Alphabet Simulation", "instructor_email": "d@g.com"},
    {"name": "Paya Simulation", "instructor_email": "p@g.com"},
    {"name": "Shopify Simulation", "instructor_email": "d@g.com"},
]

teams = [
    {"name": "Google", "simulation_class_name": "Alphabet Simulation"},
    {"name": "Decoease", "simulation_class_name": "Paya Simulation"},
    {"name": "Giftit", "simulation_class_name": "Shopify Simulation"},
]

players = [
    {"player_email": "h@g.com", "team_name": "Google"},
    {"player_email": "m@g.com", "team_name": "Decoease"},
    {"player_email": "a@g.com", "team_name": "Giftit"},
]

dynamic_rd = [
    {
        "player_email": "h@g.com",
        "category": RDCategories.BASIC,
        "order": 1,
        "started_at": 1,
        "time_spent_developing": 1,
        "run_at_quarter": 2,
        "alias": "SuperSonic Jetpack",
        "icon_link": "https://cdn.hubro.com/img/SuperSonicJetpack.png",
        "engine": 1,
        "chassis": 2,
        "strap": 0,
        "engine_color": 5,
        "chassis_color": 11,
        "strap_color": 7,
    },
    {
        "player_email": "h@g.com",
        "category": RDCategories.BASIC,
        "order": 2,
        "started_at": 2,
        "run_at_quarter": 2,
        "time_spent_developing": 0,
    },
    {
        "player_email": "h@g.com",
        "category": RDCategories.PRODUCTION,
        "order": 1,
        "started_at": 2,
        "run_at_quarter": 2,
        "time_spent_developing": 0,
    },
]
