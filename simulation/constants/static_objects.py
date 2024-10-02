from ..models.finance import FinancialAccount
from ..models.simulation import RnDStatic

RnD_statics = [
    {
        "type": RnDStatic.RnDTypes.PRODUCT,
        "title": "Basic jetpack",
        "product_key": RnDStatic.ProductKeys.BASIC,
        "development_cost": 5000000,
        "depreciation_time": 12,
        "original_unit_mat_cost": 10000,
        "development_duration": 1,
        "description": r"The cheapest configuration of a jetpack available, for those who just need the bare minimum. Adds the ability to produce Basic jetpacks",
    },
    {
        "type": RnDStatic.RnDTypes.UPGRADE,
        "title": "Waste reduction",
        "product_key": RnDStatic.ProductKeys.BASIC,
        "development_cost": 8000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Reduce material usage by 10 % of original usage through improved inventory handling and better quality control.",
    },
    {
        "type": RnDStatic.RnDTypes.UPGRADE,
        "title": "Lightweight construction",
        "product_key": RnDStatic.ProductKeys.BASIC,
        "development_cost": 16000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Develop a new, lighter chassis that reduces material usage by an additional 20 % of the original usage.",
    },
    {
        "type": RnDStatic.RnDTypes.UPGRADE,
        "title": "Substitute materials",
        "product_key": RnDStatic.ProductKeys.BASIC,
        "development_cost": 12000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Replace the standard materials with a nano-mesh material, resulting in an additional 15 % material usage reduction of the original usage.",
    },
    {
        "type": RnDStatic.RnDTypes.PRODUCT,
        "title": "Sporty jetpack",
        "product_key": RnDStatic.ProductKeys.SPORTY,
        "development_cost": 15000000,
        "depreciation_time": 12,
        "original_unit_mat_cost": 16000,
        "development_duration": 2,
        "description": r"Only the best is good enough, the strongest engines and the most durable materials. Adds the ability to produce Sporty Jetpacks.",
    },
    {
        "type": RnDStatic.RnDTypes.UPGRADE,
        "title": "Waste reduction",
        "product_key": RnDStatic.ProductKeys.SPORTY,
        "development_cost": 8000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Reduce material usage by 10 % of original usage through improved inventory handling and better quality control.",
    },
    {
        "type": RnDStatic.RnDTypes.UPGRADE,
        "title": "Lightweight construction",
        "product_key": RnDStatic.ProductKeys.SPORTY,
        "development_cost": 16000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Develop a new, lighter chassis that reduces material usage by an additional 20 % of the original usage.",
    },
    {
        "type": RnDStatic.RnDTypes.UPGRADE,
        "title": "Substitute materials",
        "product_key": RnDStatic.ProductKeys.SPORTY,
        "development_cost": 12000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Replace the standard materials with a nano-mesh material, resulting in an additional 15 % material usage reduction of the original usage.",
    },
    {
        "type": RnDStatic.RnDTypes.PRODUCT,
        "title": "Safe jetpack",
        "product_key": RnDStatic.ProductKeys.SAFE,
        "development_cost": 7000000,
        "depreciation_time": 12,
        "original_unit_mat_cost": 14000,
        "development_duration": 2,
        "description": r"Includes parachutes, helmets and advanced AI to avoid collisions. Adds the ability to produce Safe jetpacks",
    },
    {
        "type": RnDStatic.RnDTypes.UPGRADE,
        "title": "Waste reduction",
        "product_key": RnDStatic.ProductKeys.SAFE,
        "development_cost": 8000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Reduce material usage by 10 % of original usage through improved inventory handling and better quality control.",
    },
    {
        "type": RnDStatic.RnDTypes.UPGRADE,
        "title": "Lightweight construction",
        "product_key": RnDStatic.ProductKeys.SAFE,
        "development_cost": 16000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Develop a new, lighter chassis that reduces material usage by an additional 20 % of the original usage.",
    },
    {
        "type": RnDStatic.RnDTypes.UPGRADE,
        "title": "Substitute materials",
        "product_key": RnDStatic.ProductKeys.SAFE,
        "development_cost": 12000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Replace the standard materials with a nano-mesh material, resulting in an additional 15 % material usage reduction of the original usage.",
    },
    {
        "type": RnDStatic.RnDTypes.PRODUCT,
        "title": "Green jetpack",
        "product_key": RnDStatic.ProductKeys.GREEN,
        "development_cost": 10000000,
        "depreciation_time": 12,
        "original_unit_mat_cost": 12000,
        "development_duration": 3,
        "description": r"Runs on renewable energy sources, and is made of 100% recyclable materials. Adds the ability to produce Green jetpacks",
    },
    {
        "type": RnDStatic.RnDTypes.UPGRADE,
        "title": "Waste reduction",
        "product_key": RnDStatic.ProductKeys.GREEN,
        "development_cost": 8000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Reduce material usage by 10 % of original usage through improved inventory handling and better quality control.",
    },
    {
        "type": RnDStatic.RnDTypes.UPGRADE,
        "title": "Lightweight construction",
        "product_key": RnDStatic.ProductKeys.GREEN,
        "development_cost": 16000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Develop a new, lighter chassis that reduces material usage by an additional 20 % of the original usage.",
    },
    {
        "type": RnDStatic.RnDTypes.UPGRADE,
        "title": "Substitute materials",
        "product_key": RnDStatic.ProductKeys.GREEN,
        "development_cost": 12000000,
        "depreciation_time": 12,
        "development_duration": 1,
        "description": r"Replace the standard materials with a nano-mesh material, resulting in an additional 15 % material usage reduction of the original usage.",
    },
    {
        "type": RnDStatic.RnDTypes.UPGRADE,
        "title": "Sustainable components",
        "product_key": RnDStatic.ProductKeys.PRODUCTION,
        "development_cost": 5000000,
        "development_duration": 1,
        "description": r"Many of the parts in your jetpacks are today made from non-renewable materials like plastics, oils and other petrol-based products. Now a company called Green Chain offers to substitute every fossil-based part of your jetpacks with natural materials, such as biopolymers and natural oils. By investing in this project, Green Chain will map our production line and make changes that will substitute each fossil-based component with a nature-based component. The project only has a one-time cost and will not affect your variable costs. Reduces production emissions by 20 % points.",
    },
    {
        "type": RnDStatic.RnDTypes.UPGRADE,
        "title": "Waste material recycling",
        "product_key": RnDStatic.ProductKeys.PRODUCTION,
        "development_cost": 7000000,
        "development_duration": 1,
        "description": r"Re-use or sell cutoffs and waste materials from manufacturing processes. Reduces production emissions by 20 % points.",
    },
    {
        "type": RnDStatic.RnDTypes.UPGRADE,
        "title": "Heat energy recovery",
        "product_key": RnDStatic.ProductKeys.PRODUCTION,
        "development_cost": 8500000,
        "development_duration": 1,
        "description": r"Capture heat energy for re-use in manufacturing processes and for energy generation. Reduces production emissions by 25% points.",
    },
    {
        "type": RnDStatic.RnDTypes.UPGRADE,
        "title": "Local energy production",
        "product_key": RnDStatic.ProductKeys.PRODUCTION,
        "development_cost": 10000000,
        "development_duration": 1,
        "description": r"Install solar panels and wind production units on factory premises. Reduces production emissions by 35% points.",
    },
]


financial_accounts = [
    {
        "name": FinancialAccount.AccountNames.DEPRECIATION_OF_FACTORIES,
        "type": FinancialAccount.AccountTypes.DEBIT
    },
    {
        "name": FinancialAccount.AccountNames.FACTORIES,
        "type": FinancialAccount.AccountTypes.DEBIT
    },
    {
        "name": FinancialAccount.AccountNames.AMORTIZATION,
        "type": FinancialAccount.AccountTypes.DEBIT
    },
    {
        "name": FinancialAccount.AccountNames.RESEARCHED_TECHNOLOGY,
        "type": FinancialAccount.AccountTypes.DEBIT
    },
    {
        "name": FinancialAccount.AccountNames.DIRECT_LABOR,
        "type": FinancialAccount.AccountTypes.DEBIT
    },
    {
        "name": FinancialAccount.AccountNames.DIRECT_RAW_MATERIALS,
        "type": FinancialAccount.AccountTypes.DEBIT
    },
    {
        "name": FinancialAccount.AccountNames.FINISHED_GOODS_INVENTORY,
        "type": FinancialAccount.AccountTypes.DEBIT
    },
    {
        "name": FinancialAccount.AccountNames.STORAGE,
        "type": FinancialAccount.AccountTypes.DEBIT
    },
    {
        "name": FinancialAccount.AccountNames.CASH,
        "type": FinancialAccount.AccountTypes.DEBIT
    },
    {
        "name": FinancialAccount.AccountNames.CURRENT_PORTION_OF_LOANS_PAYABLE,
        "type": FinancialAccount.AccountTypes.CREDIT
    },
    {
        "name": FinancialAccount.AccountNames.INTEREST_EXPENSES,
        "type": FinancialAccount.AccountTypes.DEBIT
    },
    {
        "name": FinancialAccount.AccountNames.MAINTENANCE,
        "type": FinancialAccount.AccountTypes.DEBIT
    },
    {
        "name": FinancialAccount.AccountNames.PROMOTION,
        "type": FinancialAccount.AccountTypes.DEBIT
    },
    {
        "name": FinancialAccount.AccountNames.SALES,
        "type": FinancialAccount.AccountTypes.CREDIT
    },
    {
        "name": FinancialAccount.AccountNames.OVERDRAFT,
        "type": FinancialAccount.AccountTypes.CREDIT
    },
    {
        "name": FinancialAccount.AccountNames.LONG_TERM_NOTES_PAYABLE,
        "type": FinancialAccount.AccountTypes.CREDIT
    },
    {
        "name": FinancialAccount.AccountNames.RAW_MATERIAL_INVENTORY,
        "type": FinancialAccount.AccountTypes.DEBIT
    }
] 