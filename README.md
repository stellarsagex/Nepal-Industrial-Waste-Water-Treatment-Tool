An engineering-grade, multi-objective computational framework built to simulate, evaluate, and optimize industrial wastewater treatment trains for multiple industries in Nepal. The system evaluates 138 unique process configurations, verifies chemical mass balances, maps structural asset sizing, and ranks feasible paths against the Nepal Gazette Generic Industrial Effluent Discharge Standards.

TO ADD NEW UNITS:
To introduce a brand new process unit—such as an Advanced Oxidation Process (AOP / Fenton's Reagent) module—into the framework, we need to update five files across our directory structure. Here is the exact step-by-step checklist of what files to change and update:

Step 1: Create the Unit Sizing Model📂 File: units/aop.py (New File)
What to do: Create a new Python file inside the units/ directory following the standard unit interface.
What it contains: Implement a class (e.g., class AdvancedOxidation:) containing methods to compute:calculate_volume() and calculate_land()calculate_removals(influent) (highly efficient for Color and COD)calculate_chemical_dose(influent) (for Fenton's: Hydrogen Peroxide H₂O₂ and Ferrous Sulfate FeSO₄)calculate_sludge(influent) (Fenton's produces chemical iron sludge)calculate_energy(), calculate_capex(), and calculate_opex(influent)design(influent) returning the standard data output schema dictionary.

Step 2: Add Sizing and Performance Assumptions📂 File: config/design_criteria.py (Update)
What to do: Add a new dictionary block to track the raw sizing variables for your new unit.
Example Additions:python"AOP": {
    "hrt_hr": 2.0,
    "depth_m": 3.0,
    "pump_kw": 2.2,
    "h2o2_dose_mgL": 150.0,
    "feso4_dose_mgL": 300.0,
    "cod_removal": 0.85,
    "color_removal": 0.95,
    "bod_removal": 0.10,
    "tss_removal": -0.20  # Fenton's precipitation can increase solids before clarifiers!
}

Step 3: Add Chemical Pricing or Equipment Rates📂 File: config/economics.py (Update)
What to do: If the new unit uses any new reagents or specific equipment constants, register them here to keep pricing centralized.
Example Additions: Add "Hydrogen_Peroxide": 120 and "Ferrous_Sulfate": 45 inside the ECONOMICS["chemicals"] dictionary block.

Step 4: Register the Class in the Simulator📂 File: simulator/process_simulator.py (Update)
What to do:Add an import statement at the top of the file: from units.aop import AdvancedOxidationMap it into the centralized UNIT_REGISTRY dictionary so the engine can instantiate it:pythonUNIT_REGISTRY = {
    ...
    "AOP": AdvancedOxidation
}

Step 5: Incorporate the Unit Into Search Matrix📂 File: optimizer/train_generator.py (Update)
What to do: Tell the optimization matrix where this unit physically fits in a treatment plant.
How to update:If it's a tertiary polishing step, add "AOP" into the self.tertiary_options list framework.
If it can act as a secondary treatment path, add it to self.biological_units (or create an advanced chemical option loop block).
Enforce any process safety engineering constraints inside generate() 
(e.g., “If AOP is selected, a Sand_Filter or Clarifier must follow it to filter out precipitated iron flocs.”).
