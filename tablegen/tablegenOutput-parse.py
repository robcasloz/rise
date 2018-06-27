#!/usr/bin/env python

import yaml
import pyparsing as pp
import re
import time
import sys

#Separate file containing names of all instructions used in Unison
from unison_instructions import unisonInstructions

def main():
    print ("Main here!")


    #Define parser running on stdin
    instructionToken = pp.SkipTo("{")
    schedRWToken = pp.SkipTo(";")
    instructionParser = pp.Suppress("def") + instructionToken("Instruction") + pp.SkipTo("list<SchedReadWrite>SchedRW=") + pp.Suppress("list<SchedReadWrite>SchedRW=") + schedRWToken("SchedRWGroups") 
    
    defs = ReadIn() 
    print("Finished reading from input")
    instructions = []
    #Read from stdin, and create whitespace-free string on single line
    for instruction in instructionParser.searchString(defs):
        instructions.append(instruction.asDict())
        print(instruction.asDict())

    # print(instructions)

    #We want to skip all input up until "------------- Defs -----------------"



def ReadIn():
    inLines = sys.stdin.readlines()
    defsReached = False
    defs = ""

    #Find the defs from the output, which is all we want
    for line in inLines:
        line = line.strip('\n')
        if (not defsReached) and (line == "------------- Defs -----------------"):
            print("found defs")
            defsReached = True
        elif defsReached:
            defs += line.replace('\t', '').replace(' ', '').strip()

    return defs
    


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))

