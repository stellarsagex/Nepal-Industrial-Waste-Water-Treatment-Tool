"""
design_criteria.py

Central design criteria database.

All units pull sizing and performance
assumptions from here.

Units should NEVER hard-code design
parameters internally.
"""

DESIGN_CRITERIA = {

    # ==========================================
    # EQUALIZATION
    # ==========================================

    "Equalization": {

        "hrt_hr": 6.0,
        "depth_m": 3.0,
        "mixing_power_kw_m3": 0.005
    },

    # ==========================================
    # NEUTRALIZATION
    # ==========================================

    "Neutralization": {

        "hrt_hr": 1.0,
        "depth_m": 3.0,
        "target_ph": 7.0,
        "mixing_power_kw_m3": 0.01
    },

    # ==========================================
    # COAGULATION
    # ==========================================

    "Coagulation": {

        "rapid_mix_hr": 0.05,
        "flocculation_hr": 0.35,
        "depth_m": 3.0,
        "rapid_mix_kw_m3": 0.015,
        "floc_kw_m3": 0.005,

        "tss_removal": 0.65,
        "color_removal": 0.55,
        "cod_removal": 0.30,
        "bod_removal": 0.20,
        "oil_removal": 0.85       # Added to resolve framework oil constraint failures
    },

    # ==========================================
    # PRIMARY CLARIFIER
    # ==========================================

    "Primary_Clarifier": {

        "surface_overflow_rate": 25.0,
        "depth_m": 3.0,
        "scraper_power_kw": 0.75,

        "tss_removal": 0.60,
        "bod_removal": 0.30,
        "cod_removal": 0.20,
        "oil_removal": 0.70       # Added to resolve framework oil constraint failures
    },

    # ==========================================
    # ABR
    # ==========================================

    "ABR": {

        "hrt_hr": 24.0,
        "depth_m": 4.0,
        "pump_kw": 1.5,
        
        "bod_removal": 0.85,
        "cod_removal": 0.80,
        "tss_removal": 0.65,

        "methane_yield": 0.25,
        "biomass_yield": 0.10
    },

    # ==========================================
    # UASB
    # ==========================================

    "UASB": {

        "hrt_hr": 12.0,
        "depth_m": 6.0,
        "pump_kw": 2.2,

        "bod_removal": 0.88,
        "cod_removal": 0.85,
        "tss_removal": 0.70,

        "methane_yield": 0.30,
        "biomass_yield": 0.08
    },

    # ==========================================
    # ASP
    # ==========================================

    "ASP": {

        "hrt_hr": 8.0,
        "depth_m": 4.0,
        "pump_kw": 3.0,
        "aeration_kwh_per_kg_bod": 1.2,
        "yield_factor": 0.60,

        "bod_removal": 0.93,
        "cod_removal": 0.80,
        "tss_removal": 0.85,
        "color_removal": 0.20
    },

    # ==========================================
    # MBBR
    # ==========================================

    "MBBR": {

        "hrt_hr": 6.0,
        "depth_m": 4.0,
        "mixing_kw": 1.5,
        "media_fill_fraction": 0.55,
        "aeration_kwh_per_kg_bod": 1.0,
        "yield_factor": 0.45,

        "bod_removal": 0.92,
        "cod_removal": 0.80,
        "tss_removal": 0.70,
        "color_removal": 0.15
    },

    # ==========================================
    # SBR
    # ==========================================

    "SBR": {

        "hrt_hr": 10.0,
        "depth_m": 4.5,
        "mixing_kw": 2.0,
        "aeration_kwh_per_kg_bod": 1.1,
        "yield_factor": 0.50,

        "bod_removal": 0.95,
        "cod_removal": 0.85,
        "tss_removal": 0.90,
        "color_removal": 0.25
    },

    # ==========================================
    # WETLAND
    # ==========================================

    "Wetland": {

        "hydraulic_loading": 0.04,
        "depth_m": 0.6,
        "pump_kw": 0.37,

        "bod_removal": 0.80,
        "cod_removal": 0.60,
        "tss_removal": 0.75,
        "color_removal": 0.40
    },

    # ==========================================
    # SAND FILTER
    # ==========================================

    "Sand_Filter": {

        "filtration_rate": 5.0,
        "depth_m": 2.0,
        "pump_kw": 1.1,

        "tss_removal": 0.50,
        "bod_removal": 0.05,
        "cod_removal": 0.05,
        "color_removal": 0.10
    },

    # ==========================================
    # ACTIVATED CARBON
    # ==========================================

    "Activated_Carbon": {

        "ebct_hr": 0.5,
        "bed_depth_m": 2.5,
        "pump_kw": 1.5,
        "carbon_density_kg_m3": 500.0,
        "adsorption_capacity": 0.25,

        "bod_removal": 0.10,
        "cod_removal": 0.75,
        "tss_removal": 0.20,
        "color_removal": 0.85
    },

    # ==========================================
    # RO
    # ==========================================

    "RO": {

        "recovery": 0.75,
        "flux_lmh": 15.0,
        "specific_energy_kwh_m3": 1.8,

        "tds_removal": 0.97,
        "color_removal": 0.99,
        "cod_removal": 0.95,
        "bod_removal": 0.98,
        "tss_removal": 0.99
    },

    # ==========================================
    # SLUDGE FILTER PRESS
    # ==========================================
    "Filter_Press": {
        "feed_solids_fraction": 0.03,      # 3% solids content in incoming secondary wet sludge
        "cake_solids_fraction": 0.35,      # 35% bone-dry solid cake consistency after press cycle
        "cycle_time_hr": 4.0,              # Operational batch turnaround time footprint
        "chamber_thickness_mm": 32.0,      # Thickness parameter boundary
        "power_kw_per_kg_solids": 0.02     # Hydraulic piston motor efficiency constant
    },

    # Dissolved Air Floatation
    "DAF": {
        "loading_rate_m3_m2_hr": 5.0,
        "depth_m": 2.5,
        "compressor_power_kw": 2.2,
        "oil_removal": 0.92,
        "tss_removal": 0.60,
        "cod_removal": 0.25,
        "bod_removal": 0.20
    },

    #advanced oxidation process
    "AOP": {
        "hrt_hr": 2.0,
        "depth_m": 3.5,
        "h2o2_mg_per_mg_cod": 1.0,
        "feso4_mg_per_mg_cod": 2.0,
        "mixer_kw_m3": 0.012,
        "color_removal": 0.90,
        "cod_removal": 0.75,
        "bod_removal": 0.15
    },
    #Sludge drying bed
    "Sludge_Drying_Bed": {
        "solids_loading_kg_m2_year": 120.0,
        "cake_solids_fraction": 0.30,
        "feed_solids_fraction": 0.03
    },


}
