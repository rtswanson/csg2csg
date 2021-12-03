#!/usr/env/python3

from csg2csg.MaterialCard import MaterialCard
from csg2csg.MaterialData import ThermalScattering, MCNP_XSDATA
from csg2csg.MCNPFormatter import get_fortran_formatted_number

import sys

# writes an mcnp material card given the generic description
def write_mcnp_material(filestream, Material, preserve_xs):

    filestream.write("C Material " + str(Material.material_name) + "\n")
    filestream.write("M"+ str(Material.material_number))
    for nucid in Material.composition_dictionary:
        string = "     " + str(nucid)
        if preserve_xs:
            string += "." + str(Material.xsid_dictionary[nucid])
        string += " " + str(Material.composition_dictionary[nucid]) + "\n"
        filestream.write(string)
    return

# Class to handle MCNP Material Card
class MCNPMaterialCard(MaterialCard):
    
    def __init__(self, material_number, card_string):
        MaterialCard.__init__(self, material_number, card_string)
        self.material_name = "M"+str(material_number)
        self.material_number = material_number
        self.__process_string()

    # populate the MCNP Material Card
    def __process_string(self):
        # need to reset the dictionary
        # otherwise state seems to linger - weird
        self.composition_dictionary = {}
        self.xsid_dictionary = {}
        self.xsid_temperature = {}

        mat_string = self.text_string
        mat_string = mat_string.replace("\n","")
        
        # split string
        all_tokens = mat_string.split()

        # need to remove other material keywords not zaids
        tokens = []
        keywords = []
        for token in all_tokens:
            if "=" in token:
                keywords.append(token)
            else:
                tokens.append(token)

        if len(tokens)%2 != 0:
            print ("Material string not correctly processed")
            sys.exit(1)
        while len(tokens) != 0:
            nuclide = tokens[0].split(".")
            nucid = nuclide[0]
            try:
                xsid = nuclide[1]
            except:
                xsid = ""

            frac = get_fortran_formatted_number(tokens[1])
            tokens.pop(0)
            tokens.pop(0)
            if nucid in self.composition_dictionary.keys():
                self.composition_dictionary[nucid] += frac
            else:
                self.composition_dictionary[nucid] = frac
            self.xsid_dictionary[nucid] = xsid

            # lookup zaid and suffix, find temperature, default to 293.6 if not found
            xs_temp = MCNP_XSDATA.entries[MCNP_XSDATA.entries["ZAID"] == nucid + "." + xsid]["T(K)"]
            if len(xs_temp) == 0:
                print("Warning: Could not find {} in xsdir file".format(nucid + "." + xsid))
                self.xsid_temperature[nucid] = 293.6
            else:
                self.xsid_temperature[nucid] = xs_temp.values[0]

        # calculate weighted temperature
        ave_temp = (sum([self.xsid_temperature[nucid]*float(self.composition_dictionary[nucid]) for nucid in self.xsid_temperature]) /
                    sum(list(map(float,self.composition_dictionary.values()))))
        self.temperature = ave_temp

        return


class MCNPSABCard(MaterialCard):
    
    def __init__(self, material_number, card_string):
        MaterialCard.__init__(self, material_number, card_string)
        self.material_name = "MT"+str(material_number)
        self.material_number = material_number
        self.__process_string()

    # populate the MCNP Material Card
    def __process_string(self):
        # need to reset the list
        # otherwise state seems to linger - weird
        self.thermal_scattering = []

        mat_string = self.text_string
        mat_string = mat_string.replace("\n","")
        
        # split string
        tokens = mat_string.split()

        while len(tokens) != 0:
            sab = tokens[0].split(".")[0]

            tokens.pop(0)

            scattering = ThermalScattering()

            self.thermal_scattering.append( scattering.generalise[sab] )
        return