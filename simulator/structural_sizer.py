"""
Structural Sizer Module

Translates calculated operational volumes and areas from process unit designs
into concrete structural dimensions (Length, Width, Diameter, Height, Freeboard).
Includes clean output tracking formats for specialized mechanical filtration skids.
"""

import math
from config.design_criteria import DESIGN_CRITERIA

class StructuralSizer:

    def __init__(self):
        self.default_freeboard = 0.5  # meters
        self.default_l_w_ratio = 2.0  # Length-to-Width ratio for rectangular tanks

    def size_unit(self, unit_name, design_output):
        """
        Computes physical dimensions based on unit geometry types.
        """
        design_data = design_output.get("design", {})
        volume = design_data.get("volume_m3", 0)
        area = design_data.get("filter_area_m2", design_data.get("surface_area_m2", 0))
        
        criteria = DESIGN_CRITERIA.get(unit_name, {})
        water_depth = criteria.get("depth_m", 3.0)
        freeboard = self.default_freeboard
        total_height = water_depth + freeboard

        if volume == 0 and area > 0:
            volume = area * water_depth

        # --- Geometry Type 0: Specialized Skid Mounted Filtration Systems ---
        if unit_name == "RO":
            membrane_area = design_data.get("membrane_area_m2", 0)
            permeate_flow = design_data.get("permeate_flow_m3_day", 0)
            reject_flow = design_data.get("reject_flow_m3_day", 0)
            
            # Approximate standard industrial pressure vessel rack dimensions based on membrane area
            rack_width = 1.8
            rack_length = max(2.5, round(membrane_area * 0.05, 2))
            rack_height = 2.2
            
            return {
                "geometry": "Mechanical Skid-Mounted High Pressure Membrane Rack Assembly",
                "dimensions": {
                    "Total Membrane Surface Area (m²)": round(membrane_area, 2),
                    "Permeate Reuse Yield (m³/day)": round(permeate_flow, 2),
                    "Brine Reject Stream Flow (m³/day)": round(reject_flow, 2),
                    "Approx. Physical Skid Length (m)": rack_length,
                    "Approx. Physical Skid Width (m)": rack_width,
                    "Approx. Physical Skid Height (m)": rack_height,
                    "Operational Layout Sizing Note": "Requires flat, reinforced indoor concrete floor slab."
                }
            }

        if volume == 0:
            return {"geometry": "Skipped/Non-tank structure", "dimensions": "N/A"}

        # --- Geometry Type 1: Circular Tanks ---
        if unit_name in ["Primary_Clarifier", "Secondary_Clarifier"]:
            calc_area = volume / water_depth if area == 0 else area
            diameter = math.sqrt((4 * calc_area) / math.pi)
            
            return {
                "geometry": "Circular RCC Tank",
                "dimensions": {
                    "Diameter (m)": round(diameter, 2),
                    "Water Depth (m)": round(water_depth, 2),
                    "Freeboard (m)": round(freeboard, 2),
                    "Total Tank Height (m)": round(total_height, 2),
                    "Volume (m³)": round(volume, 2)
                }
            }

        # --- Geometry Type 2: Rapid Filters (Modular Footprints) ---
        elif unit_name in ["Sand_Filter", "Activated_Carbon"]:
            calc_area = area if area > 0 else (volume / water_depth)
            cell_area = calc_area / 2  
            width = math.sqrt(cell_area / self.default_l_w_ratio)
            length = width * self.default_l_w_ratio
            
            return {
                "geometry": "Dual-Cell Rectangular Filter Bed Structure",
                "dimensions": {
                    "Number of Filter Cells": 2,
                    "Cell Length (m)": round(length, 2),
                    "Cell Width (m)": round(width, 2),
                    "Filter Media Bed Depth (m)": round(water_depth * 0.6, 2),
                    "Total Structure Height (m)": round(total_height, 2),
                    "Total Surface Filter Area (m²)": round(calc_area, 2)
                }
            }

        # --- Geometry Type 3: Standard Rectangular Tanks (ABR, ASP, Equalization, etc.) ---
        else:
            calc_area = volume / water_depth
            width = math.sqrt(calc_area / self.default_l_w_ratio)
            length = width * self.default_l_w_ratio
            
            baffles = criteria.get("compartments", 1)
            baffle_note = f"Divided into {baffles} internal baffled compartments" if baffles > 1 else "Single open-basin layout"

            return {
                "geometry": "Rectangular RCC Tank Structure",
                "dimensions": {
                    "Length (m)": round(length, 2),
                    "Width (m)": round(width, 2),
                    "Water Depth (m)": round(water_depth, 2),
                    "Freeboard (m)": round(freeboard, 2),
                    "Total Concrete Wall Height (m)": round(total_height, 2),
                    "Internal Configuration": baffle_note,
                    "Total Volumetric Space (m³)": round(volume, 2)
                }
            }
