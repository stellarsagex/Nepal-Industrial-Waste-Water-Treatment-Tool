"""
CAD Generator Module (Definitive Multi-Version Edition)

Translates calculated geometric structural sizing arrays from the sizer module
into a physical, scaled 2D AutoCAD-ready .dxf architectural blueprint file.
Insulated against ezdxf layer table modification changes.
"""

import os
import ezdxf

class CADGenerator:

    def __init__(self):
        # Setup an output directory for CAD files inside the repository folder matrix
        self.output_dir = "cad_outputs"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_blueprint(self, structural_components, industry_name):
        """
        Creates a scaled 2D layout drawing of the treatment plant.
        Tanks are drawn sequentially with spacing buffers along a shared baseline.
        """
        # Create a new DXF R2010 drawing document layout frame
        doc = ezdxf.new("R2010")
        
        # Code 6 explicitly represents METERS in the DXF global header specification.
        doc.header["$INSUNITS"] = 6  
        
        msp = doc.modelspace()
        
        # ✔️ FIXED: Use doc.layers.add() to explicitly configure layer colors safely
        # across all modern versions of ezdxf.
        if "CONCRETE_WALLS" not in doc.layers:
            doc.layers.add("CONCRETE_WALLS", color=7)  # White/Black outlines
        if "TEXT_ANNOTATIONS" not in doc.layers:
            doc.layers.add("TEXT_ANNOTATIONS", color=3) # Green informational text

        current_x = 0.0
        spacing_buffer = 5.0  # 5-meter spacing buffer between physical concrete basins

        for comp in structural_components:
            name = comp["name"]
            dims = comp["dimensions"]

            # Skip skid-mounted non-tank structural readouts safely
            if not isinstance(dims, dict):
                continue

            # --- Layout Geometry Type 1: Rectangular Concrete Structures ---
            if "Length (m)" in dims and "Width (m)" in dims:
                length = float(dims["Length (m)"])
                width = float(dims["Width (m)"])
                
                # Draw outer concrete basin walls (Polyline box rectangle)
                points = [
                    (current_x, 0.0),
                    (current_x + length, 0.0),
                    (current_x + length, width),
                    (current_x, width),
                    (current_x, 0.0)
                ]
                msp.add_lwpolyline(points, dxfattribs={"layer": "CONCRETE_WALLS"})
                
                # Center text layout placement using lightweight flat native 2D coordinates
                text_x = current_x + (length * 0.1) # left indent buffer spacing allocation
                text_y = width * 0.5
                
                # Insertion coordinates passed cleanly as the direct parameter element
                msp.add_text(f"NODE: {name}", dxfattribs={"height": 0.35, "layer": "TEXT_ANNOTATIONS"}).set_placement((text_x, text_y))
                msp.add_text(f"SIZE: {length}m x {width}m", dxfattribs={"height": 0.25, "layer": "TEXT_ANNOTATIONS"}).set_placement((text_x, text_y - 0.5))
                
                # Advance baseline marker path layout for the next consecutive treatment unit
                current_x += length + spacing_buffer

            # --- Layout Geometry Type 2: Circular Concrete Structures (Clarifiers) ---
            elif "Diameter (m)" in dims:
                diameter = float(dims["Diameter (m)"])
                radius = diameter / 2.0
                
                center_x = current_x + radius
                center_y = radius
                
                # Draw outer circular concrete layout wall
                msp.add_circle((center_x, center_y), radius, dxfattribs={"layer": "CONCRETE_WALLS"})
                
                # Set text parameters inside circle bounds
                text_x = center_x - (radius * 0.6)
                text_y = center_y
                
                # Insertion coordinates passed cleanly as the direct parameter element
                msp.add_text(f"NODE: {name}", dxfattribs={"height": 0.35, "layer": "TEXT_ANNOTATIONS"}).set_placement((text_x, text_y))
                msp.add_text(f"DIA: {diameter}m", dxfattribs={"height": 0.25, "layer": "TEXT_ANNOTATIONS"}).set_placement((text_x, text_y - 0.5))
                
                current_x += diameter + spacing_buffer

            # --- Layout Geometry Type 3: Specialized Mechanical or Sludge Sub-Blocks ---
            elif "total_surface_area_m2" in dims:
                beds = int(dims["number_of_beds"])
                length = float(dims["cell_length_m"])
                width = float(dims["cell_width_m"])
                
                # Draw drying bed compartments sequentially
                for i in range(beds):
                    offset_y = i * (width + 2.0) # stack cells vertically with a 2m clear separation path
                    points = [
                        (current_x, offset_y),
                        (current_x + length, offset_y),
                        (current_x + length, offset_y + width),
                        (current_x, offset_y + width),
                        (current_x, offset_y)
                    ]
                    msp.add_lwpolyline(points, dxfattribs={"layer": "CONCRETE_WALLS"})
                    
                text_x = current_x + (length * 0.1)
                text_y = width * 0.5
                
                # Insertion coordinates passed cleanly as the direct parameter element
                msp.add_text(f"NODE: {name}", dxfattribs={"height": 0.35, "layer": "TEXT_ANNOTATIONS"}).set_placement((text_x, text_y))
                msp.add_text(f"BEDS: {beds} CELLS", dxfattribs={"height": 0.25, "layer": "TEXT_ANNOTATIONS"}).set_placement((text_x, text_y - 0.5))
                
                current_x += length + spacing_buffer

        # Save blueprint cleanly to disk directory records
        filename = f"wwtp_layout_{industry_name.lower()}.dxf"
        filepath = os.path.join(self.output_dir, filename)
        doc.saveas(filepath)
        return filepath
