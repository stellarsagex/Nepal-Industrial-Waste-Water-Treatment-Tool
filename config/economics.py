"""
economics.py

Central economics database.

All costs should be pulled from here.

Units, optimizer, CAPEX model and OPEX model
must not hard-code prices.
"""

ECONOMICS = {

    # ==========================================
    # ELECTRICITY
    # ==========================================

    "electricity_tariff": {

        "industrial": 13.0,      # NPR/kWh
        "commercial": 15.0
    },

    # ==========================================
    # CHEMICAL COSTS
    # ==========================================

    "chemicals": {

        "Alum": 35,                  # NPR/kg
        "PAC": 65,
        "Polymer": 900,

        "Lime": 18,
        "Caustic": 85,

        "Sulfuric_Acid": 55,
        "Hydrochloric_Acid": 70,

        "Activated_Carbon": 300,

        "Antiscalant": 250
    },

    # ==========================================
    # SLUDGE
    # ==========================================

    "sludge_disposal": {

        "transport": 3,      # NPR/kg

        "landfill": 5,       # NPR/kg

        "total": 8           # NPR/kg
    },

    # ==========================================
    # LABOUR
    # ==========================================

    "labour": {

        "operator_salary_month":

            30000,

        "supervisor_salary_month":

            50000
    },

    # ==========================================
    # MAINTENANCE
    # ==========================================

    "maintenance_factor":

        0.03,

    # ==========================================
    # CONTINGENCY
    # ==========================================

    "contingency_factor":

        0.10,

    # ==========================================
    # LAND
    # ==========================================

    "land_cost": {

        "industrial_area":

            12000,      # NPR/m²

        "rural":

            3000,

        "urban":

            25000
    },

    # ==========================================
    # EQUIPMENT UNIT COSTS
    # ==========================================

    "equipment_costs": {

        "blower_kw":

            60000,

        "pump_kw":

            40000,

        "mixer_kw":

            50000,

        "diffuser_point":

            2500
    },

    # ==========================================
    # CIVIL CONSTRUCTION
    # ==========================================

    "civil_costs": {

        "rcc_tank":

            22000,      # NPR/m³

        "clarifier":

            26000,

        "reactor":

            25000,

        "wetland":

            3500
    }
}