#!/usr/env/python3

from math import floor
import xml.etree.ElementTree as ET

def write_openmc_lattice(lattice, geometry_tree):
    # convert lattice to openmc format
    # rect lattice
    if lattice.cell_lattice_type == 1:
        # TODO should be able to grab from lattice class
        n_rings = str(int((int(lattice.cell_lattice.shape[1])+1)/2))
        n_axial = str(lattice.cell_lattice.shape[0])
        outer_text = str(lattice.cell_lattice[0,0,0])

        orientation = lattice.orientation
        
        # pitch and center
        if n_axial == "1":
            pitch_text = str(lattice.pitch[0]) + " " + str(lattice.pitch[0]) + " " + str(lattice.pitch[1])
            dimension_text = str(lattice.cell_lattice.shape[1]) + " " + str(lattice.cell_lattice.shape[2])
            lower_left_text = str(-lattice.pitch[0]*lattice.cell_lattice.shape[1]/2.) + " " + str(-lattice.pitch[0]*lattice.cell_lattice.shape[2]/2.)
        else:
            pitch_text = str(lattice.pitch[0]) + " " + str(lattice.pitch[0]) + " " + str(lattice.pitch[1])
            dimension_text = str(lattice.cell_lattice.shape[1]) + " " + str(lattice.cell_lattice.shape[2]) + " " + str(lattice.cell_lattice.shape[0])
            lower_left_text = str(-lattice.pitch[0]*lattice.cell_lattice.shape[1]/2.) + " " + str(-lattice.pitch[0]*lattice.cell_lattice.shape[2]/2.) + " " + str(-lattice.pitch[1]*lattice.cell_lattice.shape[0]/2.)
        
        # universes
        universes_text = ""
        for z in range(lattice.cell_lattice.shape[0]):
            for row in lattice.cell_lattice[z,:,:]:
                universes_text += " ".join(row.astype(str)) + "\n"

        rect_lattice = ET.SubElement(geometry_tree, "lattice", id = str(lattice.cell_universe) )

        pitch = ET.SubElement(rect_lattice, "pitch")
        pitch.text = pitch_text

        outer = ET.SubElement(rect_lattice, "outer")
        outer.text = outer_text

        dimension = ET.SubElement(rect_lattice, "dimension")
        dimension.text = dimension_text

        lower_left = ET.SubElement(rect_lattice, "lower_left")
        lower_left.text = lower_left_text

        universes = ET.SubElement(rect_lattice, "universes")
        universes.text = universes_text

    # hex lattice
    elif lattice.cell_lattice_type == 2:
        # TODO should be able to grab from lattice class
        n_rings = str(int((int(lattice.cell_lattice.shape[1])+1)/2))
        n_axial = str(lattice.cell_lattice.shape[0])
        outer_text = str(lattice.cell_lattice[0,0,0])

        orientation = lattice.orientation
        
        # pitch and center
        if n_axial == "1":
            pitch_text = str(lattice.pitch[0])
            center_text = "0.0 0.0"
        else:
            pitch_text = str(lattice.pitch[0]) + " " + str(lattice.pitch[1])
            center_text = "0.0 0.0 0.0"
        
        # universes, strip off any "padding" to put it into a square array
        # TODO change this for a "pretty" print
        half = int(floor(lattice.cell_lattice.shape[1]/2.))
        _strip_cols = list(range(half,-half-1,-1))
        universes_text = ""
        for z in range(lattice.cell_lattice.shape[0]):
            for i,row in enumerate(lattice.cell_lattice[z,:,:]):
                cols_to_strip = _strip_cols[i]
                if cols_to_strip > 0:
                    universes_text += " ".join(row[cols_to_strip:].astype(str)) + "\n"
                elif cols_to_strip == 0:
                    universes_text += " ".join(row.astype(str)) + "\n"
                else:
                    universes_text += " ".join(row[:cols_to_strip].astype(str)) + "\n"

        if n_axial == "1":
            hex_lattice = ET.SubElement(geometry_tree, "hex_lattice", id = str(lattice.cell_universe), n_rings = n_rings, orientation = orientation )
        else:
            hex_lattice = ET.SubElement(geometry_tree, "hex_lattice", id = str(lattice.cell_universe), n_axial = n_axial, n_rings = n_rings, orientation = orientation )

        pitch = ET.SubElement(hex_lattice, "pitch")
        pitch.text = pitch_text

        outer = ET.SubElement(hex_lattice, "outer")
        outer.text = outer_text

        center = ET.SubElement(hex_lattice, "center")
        center.text = center_text

        universes = ET.SubElement(hex_lattice, "universes")
        universes.text = universes_text
