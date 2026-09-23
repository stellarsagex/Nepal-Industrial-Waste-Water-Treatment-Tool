"""
standards.py

Centralized industrial effluent discharge standards database for Nepal.
Derived directly from the official Nepal Gazette statutory generic and industry-specific 
environmental protection regulations.
"""

# The active global industry focus profile for the execution pipeline matrix
ACTIVE_INDUSTRY = "Textile" 

INDUSTRIAL_STANDARDS_DATABASE = {

    # ==================================================================
    # MASTER GENERIC CODES: Discharging into Inland Surface Waters
    # ==================================================================
    "Generic_Surface": {
        "pH": {"min": 5.5, "max": 9.0},
        "BOD": {"max": 30.0},
        "COD": {"max": 250.0},
        "TSS": {"max": 50.0},
        "Oil": {"max": 10.0},
        "TDS": {"max": 2100.0},
        "Color": {"max": 150.0},
        "Temperature": {"max": 40.0}
    },

    # ==================================================================
    # MASTER GENERIC CODES: Discharging into Public Sewers
    # ==================================================================
    "Generic_Sewer": {
        "pH": {"min": 5.5, "max": 9.0},
        "BOD": {"max": 100.0},
        "COD": {"max": 400.0},
        "TSS": {"max": 150.0},
        "Oil": {"max": 50.0},
        "TDS": {"max": 2100.0},
        "Color": {"max": 250.0},
        "Temperature": {"max": 45.0}
    },

    # ==================================================================
    # SPECIFIC: Textile & Dyeing Processing Industry
    # ==================================================================
    "Textile": {
        "pH": {"min": 5.5, "max": 9.0},
        "BOD": {"max": 30.0},
        "COD": {"max": 250.0},
        "TSS": {"max": 50.0},
        "Oil": {"max": 10.0},
        "TDS": {"max": 2100.0},
        "Color": {"max": 150.0},
        "Temperature": {"max": 40.0}
    },

    # ==================================================================
    # SPECIFIC: Tanning (Leather Processing) Industry
    # ==================================================================
    "Tanning": {
        "pH": {"min": 6.0, "max": 9.0},
        "BOD": {"max": 100.0},
        "COD": {"max": 250.0},
        "TSS": {"max": 100.0},
        "Oil": {"max": 10.0},
        "TDS": {"max": 2100.0},
        "Color": {"max": 250.0},
        "Temperature": {"max": 40.0}
    },

    # ==================================================================
    # SPECIFIC: Pulp and Paper Manufacturing Industry
    # ==================================================================
    "Pulp_Paper": {
        "pH": {"min": 5.5, "max": 9.0},
        "BOD": {"max": 30.0},
        "COD": {"max": 250.0},
        "TSS": {"max": 50.0},
        "Oil": {"max": 10.0},
        "TDS": {"max": 2100.0},
        "Color": {"max": 200.0},
        "Temperature": {"max": 40.0}
    },

    # ==================================================================
    # SPECIFIC: Dairy Processing Industries
    # ==================================================================
    "Dairy": {
        "pH": {"min": 5.5, "max": 8.5},
        "BOD": {"max": 30.0},
        "COD": {"max": 250.0},
        "TSS": {"max": 50.0},
        "Oil": {"max": 20.0},
        "TDS": {"max": 2100.0},
        "Color": {"max": 150.0},
        "Temperature": {"max": 38.0}
    },

    # ==================================================================
    # SPECIFIC: Distilleries and Fermentation Industry
    # ==================================================================
    "Distillery": {
        "pH": {"min": 5.5, "max": 9.0},
        "BOD": {"max": 100.0},
        "COD": {"max": 250.0},
        "TSS": {"max": 100.0},
        "Oil": {"max": 10.0},
        "TDS": {"max": 2100.0},
        "Color": {"max": 300.0},
        "Temperature": {"max": 40.0}
    },

    # ==================================================================
    # SPECIFIC: Sugar Processing Industry
    # ==================================================================
    "Sugar": {
        "pH": {"min": 5.5, "max": 8.5},
        "BOD": {"max": 30.0},
        "COD": {"max": 250.0},
        "TSS": {"max": 50.0},
        "Oil": {"max": 10.0},
        "TDS": {"max": 2100.0},
        "Color": {"max": 150.0},
        "Temperature": {"max": 40.0}
    },
    # ==================================================================
    # SPECIFIC: Brewery
    # ==================================================================

    "Brewery": {
        "pH": {"min": 5.5, "max": 9.0},
        "BOD": {"max": 30.0},       # Nepal statutory threshold
        "COD": {"max": 250.0},
        "TSS": {"max": 50.0},
        "Oil": {"max": 10.0},
        "TDS": {"max": 2100.0},
        "Color": {"max": 150.0},
        "Temperature": {"max": 40.0}
    }

}

# Fix: Initialize as an independent working dictionary to isolate references safely
STANDARDS = dict(INDUSTRIAL_STANDARDS_DATABASE[ACTIVE_INDUSTRY])


def set_active_industry(industry_key):
    """
    Dynamically switches the active regulatory profile during runtimes without wiping the source database.
    """
    global STANDARDS, ACTIVE_INDUSTRY
    if industry_key in INDUSTRIAL_STANDARDS_DATABASE:
        ACTIVE_INDUSTRY = industry_key
        STANDARDS.clear()
        # Fix: Populates from an independent shallow copy of the source dictionary configuration records
        for k, v in INDUSTRIAL_STANDARDS_DATABASE[industry_key].items():
            STANDARDS[k] = v
        return True
    return False


def check_compliance(effluent):
    """
    Evaluates water metrics against active configuration maps.
    """
    results = {}
    for parameter, limit in STANDARDS.items():
        value = effluent.get(parameter)
        if value is None:
            results[parameter] = True
            continue

        if "min" in limit and "max" in limit:
            results[parameter] = (limit["min"] <= value <= limit["max"])
        elif "max" in limit:
            results[parameter] = (value <= limit["max"])
            
    return {"overall": all(results.values()), "details": results}


if __name__ == "__main__":
    print(f"\nActive Statutory Code Context: {ACTIVE_INDUSTRY}")
    print("Regulated Parameters and Thresholds Matrix:")
    for param, data in STANDARDS.items():
        print(f"  🔹 {param}: {data}")
