#!/usr/bin/env python

import yaml
import pyparsing as pp
import sys

#Separate file containing names of all instructions used in Unison
from unison_instructions import unisonInstructions

# Main
def main():
    tablegenDefs = extractInstructions(readIn())
    print(yaml.dump(tablegenDefs, default_flow_style=False))

# Extract each instruction outputed by tablegen and its respective SchedRW definition
def extractInstructions(tablegenDefs):
    extractedInstructions = []
    currentInstruction = ""
    currentSchedRW = None
    instructionDefined = False
    schedRWDefined = False
    firstInstruction = True
    instruction = {
            'Instruction' : None,
            'SchedRW' : None
            }
    for line in tablegenDefs:
        #Dictionary to hold definitions
        #Current line is a def of an instruction
        if line.find("def") >= 0:

            if firstInstruction:
                currentInstruction = line.split(" ")[1]
                instructionDefined = True
                firstInstruction = False
                continue

            #Found a new instruction, with earlier instruction having a defined SchedRW
            if schedRWDefined:
                instruction['Instruction'] = currentInstruction
                instruction['SchedRW'] = currentSchedRW
                extractedInstructions.append(instruction.copy())
                currentInstruction = line.split(" ")[1]
                currentSchedRW = None
                instructionDefined = True
                schedRWDefined = False

            #Found a new instruction, with earlier instruction not having a defined SchedRW
            else:
                currentInstruction = line.split(" ")[1]
                instructionDefined = True
                schedRWDefined = False

        #Current line is a schedRW that belongs to an instruction
        if line.find("list<SchedReadWrite> SchedRW") >= 0:

            #Found a second schedRW for the same instruction
            if schedRWDefined:
                raise Exception("Error while parsing! Found two defined SchedRW for same instruction: " + currentInstruction)

            #Found a schedRW that belongs to an instruction
            if instructionDefined:
                currentSchedRW = line[33:-1]
                schedRWDefined = True
                instructionDefined = False

            # Error, this is undefined behaviour as we found a SchedRW that does not belong to an instruction
            else:
                raise Exception("Error while parsing! Found a dangling SchedRW not belonging to an instruction:" + currentInstruction) 

    #Append last instruction in file as well
    if currentInstruction and currentSchedRW:
        instruction['Instruction'] = currentInstruction
        instruction['SchedRW'] = currentSchedRW
        extractedInstructions.append(instruction.copy())


    return extractedInstructions

# Read from output of tablegen and extract all the defs of instructions
def readIn():
    inLines = sys.stdin.readlines()
    defsReached = False
    defs = []

    #Find the defs from the output, which is all we want
    for line in inLines:
        line = line.strip('\n')
        if (not defsReached) and (line.find("------------- Defs -----------------") >= 0):
            defsReached = True
        elif defsReached:
            defs.append(line)

    return defs
    


if __name__ == '__main__':
    main()

