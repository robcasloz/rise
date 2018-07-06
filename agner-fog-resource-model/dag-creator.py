#!/usr/bin/env python

import itertools
import yaml
import json
import re

def main():
    stream = open('input/skylake_formated_clean.yaml', 'r')
    data = yaml.safe_load(stream)
    resources = []
    resources = getUniquePorts(data)
    dagGraph = []

    subSets = []
    #Iterate over all pairs of resources
    for resource1 in resources:

        print(resource1)

        resource = {
                'Resource' : resource1,
                'Resources' : len(removePrefix(resource1)[1:]),
                'Supersets' : []
                }

        for resource2 in resources:
            #Check if strict subset, this makes resources not point to themselves
            if set(resource1[1:]) < set(resource2[1:]):
                resource['Supersets'].append(resource2)

        dagGraph.append(resource)

    print(json.dumps(dagGraph, indent=4))



#Get unique list of port definitions
def getUniquePorts(data):
    #Get unique ports
    resources = []
    for instruction in data:
        if instruction['Uops each port'] is None or not isPortDefined(instruction['Uops each port']):
            continue
    
        portsGroups = instruction['Uops each port'].split(' ')
        for prefixPorts in portsGroups:
            ports = removePrefix(prefixPorts)
            resources.append(ports)
        
    
    return list(set(resources))


#Removes the numerical prefix (if existent) in front of ports
def removePrefix(ports):
    prefix = ports[0]
    #Remove numerical prefix
    while isNumber(prefix):
        ports = ports[1:]
        prefix = ports[0]

    return ports

#Check if a given instructions ports are defined
def isPortDefined(ports):
    #Regular expression for prefix_opt-'p'-ports-opt_whitespace, all repeated at least once
    regEx = re.compile('([\d]*[p][\d]+[\s]{0,1})+')
    regMatch = regEx.match(ports)
    if regMatch is None:
        return False
    elif regMatch.end() - regMatch.start() == len(ports):
        return True
    else:
        return False

#Remove duplicate lines in a string
def removeDuplicateEntries(listString):
    #Remove duplicate lines in list of incomplete instructions
    return '\n'.join(sorted(set(listString.split("\n")))) 

#Check if parameter is a number
def isNumber(a):
    try:
        int(a)
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    main()

