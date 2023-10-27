#!/usr/bin/env python3

####################################################################################
# project: DNAC-ComplianceMon
# module: rule_manager.py
# author: kebaldwi@cisco.com
# use case: This is the code to manage the xml files.
# developers:
#            Gabi Zapodeanu, TME, Enterprise Networks, Cisco Systems
#            Keith Baldwin, TSA, EN Architectures, Cisco Systems
#            Bryn Pounds, PSA, WW Architectures, Cisco Systems
####################################################################################

# This program is written to ingest all the XML files exported from Prime and build
# A dictionary of auditing rules to be used to check configurations

#     ------------------------------- IMPORTS -------------------------------

import os
import xmltodict

#     ----------------------------- DEFINITIONS -----------------------------

# Define a function to extract the title and description from an XML file
def parse_xml_file(file_path):
    with open(file_path) as f:
        xml_data = f.read()
    comp_rule = xmltodict.parse(xml_data)
    title = comp_rule['CustomPolicy']['Title']
    description = comp_rule['CustomPolicy'].get('Description', None)
    return title, description

