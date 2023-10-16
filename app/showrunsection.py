#!/usr/bin/env python3

####################################################################################
# project: DNAC-ComplianceMon
# module: showrunsection.py
# author: kebaldwi@cisco.com
# use case: Simple Check of XML audit files against configuration
# developers:
#            Gabi Zapodeanu, TME, Enterprise Networks, Cisco Systems
#            Keith Baldwin, TSA, EN Architectures, Cisco Systems
#            Bryn Pounds, PSA, WW Architectures, Cisco Systems
####################################################################################

# This program is written to ingest all the XML files exported from Prime and build
# A dictionary of auditing rules to be used to check configurations

#     ------------------------------- IMPORTS -------------------------------

import re

#     ----------------------------- DEFINITIONS -----------------------------

# This function pulls relevant configuration sections
def show_run_section(lines, pattern):
    try:
        pattern = re.compile(pattern)
    except ValueError:
        print("Error: Search Parameter {} not found in configuration file".format(pattern))
        exit(1)
    # Find all the lines that match the pattern
    matching_lines = []
    found_section = False
    for line in lines:
        if re.search(pattern, line):
            found_section = True
            matching_lines.append(line)
        elif found_section and line.startswith(' '):
            matching_lines.append(line)
        elif found_section and line.startswith('!'):
            matching_lines.append(line)
            found_section = False
        else:
            found_section = False
    return matching_lines    

# This function loads config sections into an array
def show_run_section_array(section_cfg):
    section_configs = []
    sections = ''.join(section_cfg)
    #print('sections\n\n',sections)
    # Use regex to split the text into sections for each interface configuration.
    keywords  = ["line vty","class","event"]
    key = ""
    for keyword in keywords:
        if re.search(keyword, sections):
            key = keyword
            break
        else:
            key = "escape_flag"
            break
    if key in sections:
        section_configs = re.split(f'({key})', sections)
        #print(section_configs)
        output_sections = []
        for i in range(0,(len(section_configs)-1)):
            if section_configs[i] == key:
                output_sections.append(section_configs[i] + section_configs[i+1])
        #print(output_sections)
        section_configs = output_sections
    else:
        section_configs = re.split(r'!\n', sections)
    #print('subsections\n\n',section_configs)
    return section_configs

# This function pulls relevant configuration sections
def show_run_headers(lines, pattern):
    try:
        pattern = re.compile(pattern)
    except ValueError:
        print("Error: Search Parameter {} not found in configuration file".format(pattern))
        exit(1)
    # Find all the lines that match the pattern
    matching_lines = []
    found_section = False
    for line in lines:
        if re.search(pattern, line):
            found_section = True
            matching_lines.append(line)
    return matching_lines    

#     ----------------------------- MAIN -----------------------------
# For testing and development purposes uncomment the code below
# calls in the body of the main program

"""
# Open the Cisco configuration file
with open('./DNAC-CompMon-Data/CSW-9300-CORE.base2hq.com_run_config.txt', 'r') as config_file:
    # Read all the lines in the file
    lines = config_file.readlines()

    # Ask the user for the regular expression pattern to search for
    pattern = input('Enter the regular expression pattern to search for: ')
    matching_lines = []
    
    #matching_lines = show_run_section(lines, pattern)

    # Print out each matching line
    #for line in matching_lines:
    #    print(line.strip("\n"))
    
    # Print the resulting array
    config_lines = show_run_section(lines, pattern)
    
    for line in config_lines:
        print(line.strip("\n"))
    
    sub_sections = show_run_section_array(config_lines)

    # print the first subsection
    test = input('Enter a number for the subsection to be displayed? ')
    print("\nSubsection: "+test+"\n\n",sub_sections[(int(test) - 1)])

    sub_sections_headers = show_run_headers(config_lines, pattern)

    #test = input('Enter a number for the subsection to be displayed? ')
    #print("\nSubsection: "+test+"\n\n",sub_sections_headers[(int(test) - 1)])
    print("\nSubsection: \n\n",sub_sections_headers)
"""
