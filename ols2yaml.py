#!/usr/bin/env python

import yaml

print("Hello world")

stream = file('skylake_formated_clean.yaml', 'r')
data = yaml.safe_load(stream)
noPorts = "Instructions without defined ports: \n"

# Print instruction names
for instruction in data:
    uOps = instruction['Uops each port']

    #Check for non-null
    if uOps:
        splitUOps = uOps.split(' ')
        cardinality = 0
        for ports in splitUOps:
            #Check if first character defines parallel ports on the form of "2p0156"
            prefix = ports[0]
            cardinality = 0
            #TODO fix prefix stuff, sometimes it is a n
            if not isinstance(prefix, int):
                print prefix
            #If there is no division prefix, just calculate cardinality
            if prefix == 'p':
                cardinality = len(ports) - 1
            #We have found a division prefix
            else:
                cardinality = len(ports) - 1 / int(prefix)
                ports = ports[1:]
                #print ports

                
                
    # Save all instructions without defined ports
    else:
        noPorts += str(instruction) + "\n"

print noPorts

