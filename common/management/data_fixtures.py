from finance.models import FinancialAccount
from people.models import CustomUser
from rd.models import StaticRD

static_rd = [
    {
        "order": 1,
        "title": "Basic jetpack",
        "category": StaticRD.Categories.BASIC,
        "type": StaticRD.RDTypes.PRODUCT,
        "development_cost": 5000000,
        "depreciation_time": 12,
        "original_unit_mat_cost": 10000,
        "development_duration": 1,
        "available_from_quarter": 1,
        "description": r"The cheapest configuration of a jetpack available, for those who just need the bare minimum. Adds the ability to produce Basic jetpacks",
    },
    {
        "order": 2,
        "title": "Waste reduction",
        "category": StaticRD.Categories.BASIC,
        "type": StaticRD.RDTypes.UPGRADE,
        "development_cost": 8000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Reduce material usage by 10 % of original usage through improved inventory handling and better quality control.",
    },
    {
        "order": 3,
        "title": "Lightweight construction",
        "category": StaticRD.Categories.BASIC,
        "type": StaticRD.RDTypes.UPGRADE,
        "development_cost": 16000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Develop a new, lighter chassis that reduces material usage by an additional 20 % of the original usage.",
    },
    {
        "order": 4,
        "title": "Substitute materials",
        "category": StaticRD.Categories.BASIC,
        "type": StaticRD.RDTypes.UPGRADE,
        "development_cost": 12000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Replace the standard materials with a nano-mesh material, resulting in an additional 15 % material usage reduction of the original usage.",
    },
    {
        "order": 1,
        "title": "Sporty jetpack",
        "category": StaticRD.Categories.SPORTY,
        "type": StaticRD.RDTypes.PRODUCT,
        "development_cost": 15000000,
        "depreciation_time": 12,
        "original_unit_mat_cost": 16000,
        "development_duration": 2,
        "available_from_quarter": 2,
        "description": r"Only the best is good enough, the strongest engines and the most durable materials. Adds the ability to produce Sporty Jetpacks.",
    },
    {
        "order": 2,
        "title": "Waste reduction",
        "category": StaticRD.Categories.SPORTY,
        "type": StaticRD.RDTypes.UPGRADE,
        "development_cost": 8000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Reduce material usage by 10 % of original usage through improved inventory handling and better quality control.",
    },
    {
        "order": 3,
        "title": "Lightweight construction",
        "category": StaticRD.Categories.SPORTY,
        "type": StaticRD.RDTypes.UPGRADE,
        "development_cost": 16000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Develop a new, lighter chassis that reduces material usage by an additional 20 % of the original usage.",
    },
    {
        "order": 4,
        "title": "Substitute materials",
        "category": StaticRD.Categories.SPORTY,
        "type": StaticRD.RDTypes.UPGRADE,
        "development_cost": 12000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Replace the standard materials with a nano-mesh material, resulting in an additional 15 % material usage reduction of the original usage.",
    },
    {
        "order": 1,
        "title": "Safe jetpack",
        "category": StaticRD.Categories.SAFE,
        "type": StaticRD.RDTypes.PRODUCT,
        "development_cost": 7000000,
        "depreciation_time": 12,
        "original_unit_mat_cost": 14000,
        "development_duration": 2,
        "available_from_quarter": 4,
        "description": r"Includes parachutes, helmets and advanced AI to avoid collisions. Adds the ability to produce Safe jetpacks",
    },
    {
        "order": 2,
        "title": "Waste reduction",
        "category": StaticRD.Categories.SAFE,
        "type": StaticRD.RDTypes.UPGRADE,
        "development_cost": 8000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Reduce material usage by 10 % of original usage through improved inventory handling and better quality control.",
    },
    {
        "order": 3,
        "title": "Lightweight construction",
        "category": StaticRD.Categories.SAFE,
        "type": StaticRD.RDTypes.UPGRADE,
        "development_cost": 16000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Develop a new, lighter chassis that reduces material usage by an additional 20 % of the original usage.",
    },
    {
        "order": 4,
        "title": "Substitute materials",
        "category": StaticRD.Categories.SAFE,
        "type": StaticRD.RDTypes.UPGRADE,
        "development_cost": 12000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Replace the standard materials with a nano-mesh material, resulting in an additional 15 % material usage reduction of the original usage.",
    },
    {
        "order": 1,
        "title": "Green jetpack",
        "category": StaticRD.Categories.GREEN,
        "type": StaticRD.RDTypes.PRODUCT,
        "development_cost": 10000000,
        "depreciation_time": 12,
        "original_unit_mat_cost": 12000,
        "development_duration": 3,
        "available_from_quarter": 8,
        "description": r"Runs on renewable energy sources, and is made of 100% recyclable materials. Adds the ability to produce Green jetpacks",
    },
    {
        "order": 2,
        "title": "Waste reduction",
        "category": StaticRD.Categories.GREEN,
        "type": StaticRD.RDTypes.UPGRADE,
        "development_cost": 8000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Reduce material usage by 10 % of original usage through improved inventory handling and better quality control.",
    },
    {
        "order": 3,
        "title": "Lightweight construction",
        "category": StaticRD.Categories.GREEN,
        "type": StaticRD.RDTypes.UPGRADE,
        "development_cost": 16000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Develop a new, lighter chassis that reduces material usage by an additional 20 % of the original usage.",
    },
    {
        "order": 4,
        "title": "Substitute materials",
        "category": StaticRD.Categories.GREEN,
        "type": StaticRD.RDTypes.UPGRADE,
        "development_cost": 12000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Replace the standard materials with a nano-mesh material, resulting in an additional 15 % material usage reduction of the original usage.",
    },
    {
        "order": 1,
        "title": "Sustainable components",
        "category": StaticRD.Categories.PRODUCTION,
        "type": StaticRD.RDTypes.UPGRADE,
        "development_cost": 5000000,
        "development_duration": 1,
        "available_from_quarter": 1,
        "description": r"Many of the parts in your jetpacks are today made from non-renewable materials like plastics, oils and other petrol-based products. Now a company called Green Chain offers to substitute every fossil-based part of your jetpacks with natural materials, such as biopolymers and natural oils. By investing in this project, Green Chain will map our production line and make changes that will substitute each fossil-based component with a nature-based component. The project only has a one-time cost and will not affect your variable costs. Reduces production emissions by 20 % points.",
    },
    {
        "order": 2,
        "title": "Waste material recycling",
        "category": StaticRD.Categories.PRODUCTION,
        "type": StaticRD.RDTypes.UPGRADE,
        "development_cost": 7000000,
        "development_duration": 1,
        "available_from_quarter": 1,
        "description": r"Re-use or sell cutoffs and waste materials from manufacturing processes. Reduces production emissions by 20 % points.",
    },
    {
        "order": 3,
        "title": "Heat energy recovery",
        "category": StaticRD.Categories.PRODUCTION,
        "type": StaticRD.RDTypes.UPGRADE,
        "development_cost": 8500000,
        "development_duration": 1,
        "available_from_quarter": 1,
        "description": r"Capture heat energy for re-use in manufacturing processes and for energy generation. Reduces production emissions by 25% points.",
    },
    {
        "order": 4,
        "title": "Local energy production",
        "category": StaticRD.Categories.PRODUCTION,
        "type": StaticRD.RDTypes.UPGRADE,
        "development_cost": 10000000,
        "development_duration": 1,
        "available_from_quarter": 1,
        "description": r"Install solar panels and wind production units on factory premises. Reduces production emissions by 35% points.",
    },
]


financial_accounts = [
    {
        "name": FinancialAccount.AccountNames.DEPRECIATION_OF_FACTORIES,
        "type": FinancialAccount.AccountTypes.DEBIT,
    },
    {
        "name": FinancialAccount.AccountNames.FACTORIES,
        "type": FinancialAccount.AccountTypes.DEBIT,
    },
    {
        "name": FinancialAccount.AccountNames.AMORTIZATION,
        "type": FinancialAccount.AccountTypes.DEBIT,
    },
    {
        "name": FinancialAccount.AccountNames.RESEARCHED_TECHNOLOGY,
        "type": FinancialAccount.AccountTypes.DEBIT,
    },
    {
        "name": FinancialAccount.AccountNames.DIRECT_LABOR,
        "type": FinancialAccount.AccountTypes.DEBIT,
    },
    {
        "name": FinancialAccount.AccountNames.DIRECT_RAW_MATERIALS,
        "type": FinancialAccount.AccountTypes.DEBIT,
    },
    {
        "name": FinancialAccount.AccountNames.FINISHED_GOODS_INVENTORY,
        "type": FinancialAccount.AccountTypes.DEBIT,
    },
    {
        "name": FinancialAccount.AccountNames.STORAGE,
        "type": FinancialAccount.AccountTypes.DEBIT,
    },
    {
        "name": FinancialAccount.AccountNames.CASH,
        "type": FinancialAccount.AccountTypes.DEBIT,
    },
    {
        "name": FinancialAccount.AccountNames.CURRENT_PORTION_OF_LOANS_PAYABLE,
        "type": FinancialAccount.AccountTypes.CREDIT,
    },
    {
        "name": FinancialAccount.AccountNames.INTEREST_EXPENSES,
        "type": FinancialAccount.AccountTypes.DEBIT,
    },
    {
        "name": FinancialAccount.AccountNames.MAINTENANCE,
        "type": FinancialAccount.AccountTypes.DEBIT,
    },
    {
        "name": FinancialAccount.AccountNames.PROMOTION,
        "type": FinancialAccount.AccountTypes.DEBIT,
    },
    {
        "name": FinancialAccount.AccountNames.SALES,
        "type": FinancialAccount.AccountTypes.CREDIT,
    },
    {
        "name": FinancialAccount.AccountNames.OVERDRAFT,
        "type": FinancialAccount.AccountTypes.CREDIT,
    },
    {
        "name": FinancialAccount.AccountNames.LONG_TERM_NOTES_PAYABLE,
        "type": FinancialAccount.AccountTypes.CREDIT,
    },
    {
        "name": FinancialAccount.AccountNames.RAW_MATERIAL_INVENTORY,
        "type": FinancialAccount.AccountTypes.DEBIT,
    },
]

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
        "category": StaticRD.Categories.BASIC,
        "order": 1,
        "started_at": 1,
        "time_spent_developing": 1,
        "run_at_quarter": 2,
        "alias": "SuperSonic Jetpack",
        "icon_link": "https://cdn.hubro.com/img/SuperSonicJetpack.png",
    },
    {
        "player_email": "h@g.com",
        "category": StaticRD.Categories.BASIC,
        "order": 2,
        "started_at": 2,
        "run_at_quarter": 2,
        "time_spent_developing": 0,
    },
    {
        "player_email": "h@g.com",
        "category": StaticRD.Categories.PRODUCTION,
        "order": 1,
        "started_at": 2,
        "run_at_quarter": 2,
        "time_spent_developing": 0,
    },
]


FACTORY_NAMES = [
        "Abbey", "Adeline", "Adrian", "Alexander", "Alice", "Amelia",
        "Benjamin", "Blake", "Brandon", "Brody",
        "Caleb", "Cameron", "Caroline", "Charles", "Charlotte", "Coralie",
        "Daniel", "David", "Diana", "Dorothy",
        "Edward", "Elena", "Elizabeth", "Emily", "Emma",
        "Felix", "Florence", "Francis", "Frederick",
        "Gabriel", "George", "Giles", "Grace",
        "Hannah", "Harper", "Harrison", "Henry",
        "Ian", "Iris", "Isaac", "Isabella",
        "Jack", "James", "Jane", "Jason", "Julia",
        "Katherine", "Kevin", "Kyle",
        "Laura", "Liam", "Lily", "Lucas", "Lucy",
        "Madison", "Mason", "Matthew", "Mia",
        "Nathan", "Nicholas", "Noah",
        "Oliver", "Olivia", "Owen",
        "Patrick", "Paul", "Peter",
        "Quinn",
        "Rachel", "Rebecca", "Robert", "Rose",
        "Samuel", "Sarah", "Sebastian", "Sophie",
        "Tanya", "Theodore", "Thomas",
        "Victoria", "Vincent",
        "Walter", "William",
        "Xavier",
        "Yasmine",
        "Zachary", "Zoe"
]