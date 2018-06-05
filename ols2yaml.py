#!/usr/bin/env python
import yaml
import hashlib
from collections import OrderedDict

def main():
    stream = open('skylake_formated_clean.yaml', 'r')
    data = yaml.safe_load(stream)
    parsed = parser(data)
    
    #Prints
    print (parsed)

#Parse the .yaml file
def parser(data):
    noPorts = "No ports: \n"
    undefPrefix = "Undefined prefixes: \n"
    noRecThro = "No reciprocal throughput defined: \n"

    # Print instruction names
    for instruction in data:
        uOps = instruction['Uops each port']
        reciprocalThroughput = instruction['Reciprocal throughput']
        recThro = True

        if not reciprocalThroughput:
            noRecThro += str(instruction) + "\n"
            recThro = False
            
    
        #Check for non-null
        if uOps and recThro:
            splitUOps = uOps.split(' ')
            cardinality = 0
            for ports in splitUOps:
                #Check if first character defines parallel ports on the form of "2p0156"
                prefix = ports[0]
                cardinality = 0
                #Standard prefix
                if (prefix == 'p'):
                    cardinality = len(ports) - 1
                #Numerical prefix
                elif isNumber(prefix):
                    ports = ports[1:]
                    #cardinality = len(ports) - 1 / int(prefix)
                #Undefined prefix
                else:
                    undefPrefix += str(instruction) + "\n"
    
        #Calculate actual throughput here
    
    
        # Save all instructions without defined ports
        else:
            noPorts += str(instruction) + "\n"

        incompleteList = removeDuplicateEntries(noPorts + undefPrefix + noRecThro) 
#        print (incompleteList)

#Remove duplicate lines in a string
def removeDuplicateEntries(listString):
    #Remove duplicate lines in list of incomplete instructions
    listString.splitlines()
    completedLinesHash = set()
    uniqueList = ""
    for line in listString:
        hashValue = hashlib.md5(line.rstrip().encode('utf-8')).hexdigest()
        if hashValue not in completedLinesHash:
            completedLinesHash.add(hashValue)
            uniqueList += line
    return uniqueList

#Check if a is a number
def isNumber(a):
    try:
        int(a)
        return True
    except ValueError:
        return False



if __name__ == "__main__":
    main()
