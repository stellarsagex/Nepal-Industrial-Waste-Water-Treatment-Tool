"""
Sludge Filter Press / Dewatering Module

Functions
---------
1. Consolidates liquid sludge mass generated across the treatment train.
2. Squeezes moisture out, translating wet mass into dense solid dry cakes.
3. Quantifies filtration area and plate count constraints.
4. Estimates mechanical CAPEX and compressed cake hauling operational costs.
"""

import math
from config.design_criteria import DESIGN_CRITERIA
from config.economics import ECONOMICS


class FilterPress:

    def __init__(self, liquid_sludge_kg_day):
        # Prevent division errors, establish a baseline mass feed
        self.sludge_load = max(liquid_sludge_kg_day, 0.1)
        
        # Pull performance assumptions from database matrix fallback blocks
        self.criteria = DESIGN_CRITERIA.get("Filter_Press", {
            "feed_solids_fraction": 0.03,      # 3% solids in raw liquid sludge feed
            "cake_solids_fraction": 0.35,      # 35% solids in compressed dry cakes
            "cycle_time_hr": 4.0,              # 4 hours per mechanical batch squeeze cycle
            "chamber_thickness_mm": 32.0,      # standard chamber thickness boundary
            "power_kw_per_kg_solids": 0.02
        })

    def calculate_cake_mass(self):
        """
        Mass Balance: Solids in = Solids out.
        The dry mass remains identical, but the total volume/wet mass drops drastically.
        """
        # Raw solid mass entering the press per day
        dry_solid_mass = self.sludge_load * self.criteria["feed_solids_fraction"]
        
        # De-watered final wet cake mass shipped out to landfill
        dewatered_cake_kg_day = dry_solid_mass / self.criteria["cake_solids_fraction"]
        return dewatered_cake_kg_day

    def calculate_volume_reduction(self):
        # Approximate water volume removed (assuming density ~1000 kg/m³)
        water_removed_m3_day = (self.sludge_load - self.calculate_cake_mass()) / 1000.0
        return max(0.0, water_removed_m3_day)

    def calculate_equipment_sizing(self):
        """
        Sizes total press volumetric chamber capacities and plate layouts.
        """
        dry_solids_per_day = self.sludge_load * self.criteria["feed_solids_fraction"]
        cycles_per_day = 24.0 / self.criteria["cycle_time_hr"]
        
        # Volume needed inside the press per single pressing cycle cycle
        cake_volume_per_cycle_m3 = (dry_solids_per_day / self.criteria["cake_solids_fraction"]) / (1100.0 * cycles_per_day)
        
        # Sizing physical plate count indexes (Assuming standard 800mm x 800mm plate metrics)
        chamber_volume_m3 = (0.8 * 0.8) * (self.criteria["chamber_thickness_mm"] / 1000.0)
        required_chambers = max(4, math.ceil(cake_volume_per_cycle_m3 / chamber_volume_m3))
        
        return {
            "chambers_count": required_chambers,
            "plates_count": required_chambers + 1,
            "chamber_volume_per_cycle_m3": cake_volume_per_cycle_m3
        }

    def calculate_energy(self):
        dry_solids_per_day = self.sludge_load * self.criteria["feed_solids_fraction"]
        return dry_solids_per_day * self.criteria["power_kw_per_kg_solids"]

    def calculate_capex(self):
        sizing = self.calculate_equipment_sizing()
        # Scale press frame and hydraulic closing piston mechanisms off the required plate count indices
        equipment_cost = sizing["plates_count"] * ECONOMICS["equipment_costs"]["pump_kw"] * 0.75
        civil_foundation = ECONOMICS["civil_costs"]["rcc_tank"] * 0.25 * 5.0  # reinforced base slab footprint
        return equipment_cost + civil_foundation

    def calculate_opex(self):
        tariff = ECONOMICS["electricity_tariff"]["industrial"]
        electricity_cost = self.calculate_energy() * tariff * 365
        
        # Dynamic Maintenance
        maintenance = self.calculate_capex() * ECONOMICS["maintenance_factor"]
        
        # CRITICAL FIX: The hauling fees apply to the compressed dry cakes, NOT the liquid sludge!
        cake_hauling_mass = self.calculate_cake_mass()
        disposal_rate = ECONOMICS["sludge_disposal"]["total"]
        hauling_cost = cake_hauling_mass * disposal_rate * 365
        
        return electricity_cost + maintenance + hauling_cost

    def design(self):
        sizing = self.calculate_equipment_sizing()
        cake_mass = self.calculate_cake_mass()
        
        return {
            "unit": "Filter_Press",
            "land_m2": 15.0, # Fixed concrete floor space footprint allocation
            "energy_kwh_day": self.calculate_energy(),
            "sludge_kg_day": cake_mass,
            "capex_npr": self.calculate_capex(),
            "opex_npr_year": self.calculate_opex(),
            "design": {
                "plates_count": sizing["plates_count"],
                "chambers_count": sizing["chambers_count"],
                "liquid_feed_kg_day": self.sludge_load,
                "cake_dry_mass_kg_day": cake_mass,
                "filtrate_water_removed_m3_day": self.calculate_volume_reduction()
            }
        }


if __name__ == "__main__":
    # Test execution using the wet sludge output weight from your recent textile optimization run
    press = FilterPress(liquid_sludge_kg_day=396.15)
    result = press.design()
    print("\n========== Sludge Filter Press Solution ==========\n")
    for k, v in result.items():
        if k != "design":
            print(f"{k}: {v}")
    print("\nChamber Hardware Metrics:")
    for k, v in result["design"].items():
        print(f"  🔹 {k}: {v}")
