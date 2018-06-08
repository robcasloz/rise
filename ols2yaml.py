#!/usr/bin/env python

import yaml
import re

def main():
    stream = open('skylake_formated_clean.yaml', 'r')
    data = yaml.safe_load(stream)
    
    #Prints
    print (parser(data))

#Parse the .yaml file
def parser(data):
    noPorts = "No ports: \n"
    undefPrefix = "Undefined prefixes: \n"
    noRecThro = "No reciprocal throughput defined: \n"
    incompleteList = "Inc. list: \n"
    resourceUsageList = "Instructions - Operands - [Resource - Resoure Usage - Hold-time]"

    # Print instruction names
    for instruction in data:
        uOps = instruction['Uops each port']
        reciprocalThroughput = instruction['Reciprocal throughput']
        resourceUsage = []

        if not reciprocalThroughput:
            noRecThro += str(instruction) + "\n"

        #Check for non-null
        if uOps:
            #Check that ports are correctly defined according to RegEx
            temp = str(isPortDefined(str(uOps)))
            if str(isPortDefined(str(uOps))) == "None":
                print("None: " + "\"" + uOps + "\"")
                print("Temp: " + temp)
            
            # print (str(uOps))
            isPortDefined(str(uOps))
            splitUOps = uOps.split(' ')
            largestCard = 0
            resource = ""

            #Get the highest port-cardinality, we need this for further calculations
            # try:
                # largestCard = largestCardinality(splitUOps, instruction)
            # except Exception as error:
                # print("Error caught: " + repr(error) + "\n" + "Instruction used: " + instruction)

            #Make the calculations
            for ports in splitUOps:
                #Check if first character defines parallel ports on the form of "2p0156"
                prefix = ports[0]
                #Standard prefix
                if (prefix == 'p'):
                    #Instruction uses LD, STA, or STD (load/store Uop)
                    if ports == "p23" or ports == "p237" or ports == "p4":
                        resource += ports + "1" + "1"
                    #Instruction is not a load/store
                    # else:

                #Numerical prefix
                elif isNumber(prefix):
                    ports = ports[1:]
                    #cardinality = len(ports) - 1 / int(prefix)
                #Undefined prefix
                else:
                    undefPrefix += str(instruction) + "\n"
        # Save all instructions without defined ports
        else:
            noPorts += str(instruction) + "\n"

        incompleteList += noPorts + undefPrefix + noRecThro 

    #Some instructions are added twice to some lists, as they brake the same rule twice. Thus we remove all duplicate entries in all lists.
    noPorts = removeDuplicateEntries(noPorts)
    undefPrefix = removeDuplicateEntries(undefPrefix)
    noRecThro = removeDuplicateEntries(noRecThro)

    #Print the list
    print (noPorts + undefPrefix + noRecThro)

#Find the largest cardinality in a string of port-definitions
def largestCardinality (ports, instruction):
    largestCard = 0
    for port in ports:
        prefix = port[0]
        #Standard prefix
        if (prefix == 'p'):
            if largestCard < len(port) - 1:
                largestCard = len(port) - 1

        #Numerical prefix
        elif(isNumber(prefix)):
            #We want the cardinality of the numbers following p
            purgeP = port.split('p')
            if largestCard < len(purgeP[1]):
                largestCard = len(purgeP[1])
            # else:
                # raise {0,1}Exception("Ports used by Uops are incorrectly defined for instruction: " + instruction)

    return largestCard


#Remove duplicate lines in a string
def removeDuplicateEntries(listString):
    #Remove duplicate lines in list of incomplete instructions
    return '\n'.join(sorted(set(listString.split("\n")))) 

#Check if a given instructions ports are defined
def isPortDefined(ports):
    #Regular expression for prefix_opt-'p'-ports-opt_whitespace, all repeated at least once
    regEx = re.compile('([\d]*[p][\d]+[\s]{0,1})+')
    match = regEx.match(ports)
    return match

#Check if parameter is a number
def isNumber(a):
    try:
        int(a)
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    main()
