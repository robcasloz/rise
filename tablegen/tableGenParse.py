#!/usr/bin/env python

import yaml
import pyparsing as pp
import re

#Separate file with a list containing all x86 instructions defined for unison
from unison_instructions import unisonInstructions

def main():
    #Transform string of unison instructions to a list of strings with individual instructions
    uniInstr = unisonInstructions.replace("\n", '')
    uniInstr = uniInstr.replace("\t", '')
    uniInstr = uniInstr.replace(" ", '')
    uniInstr = uniInstr.split(",")


    #Parser to find each regex-instructions that belongs to a SKLWriteResGroup
    writeResGroup = pp.Word(pp.alphanums)
    instRegex = pp.SkipTo("\"")
    instrGroupDef = pp.Suppress("def: InstRW<[") + writeResGroup("SKLWriteResGroup") + pp.Suppress("], (instregex \"") + instRegex("Regex") + pp.Suppress("\")>;")

    #Parser to find each SKLWriteResGroup definition
    ports = pp.SkipTo("]")
    latency = pp.Word(pp.nums)
    microOps = pp.Word(pp.nums)
    resourceCycles = pp.SkipTo("]")
    sKLWriteResGroupDef = pp.Suppress("def ") + writeResGroup("SKLWriteResGroup") + pp.Suppress(": SchedWriteRes<[") + ports("Ports") + pp.Suppress(pp.restOfLine) + (
            pp.Suppress("let Latency = ") + latency("Latency")  + pp.Suppress(pp.restOfLine) +
            pp.Suppress("let NumMicroOps = ") + microOps("NumMicroOps") + pp.Suppress(pp.restOfLine) + 
            pp.Suppress("let ResourceCycles = [") + resourceCycles("ResourceCycles") + pp.Suppress(pp.restOfLine)
        )

    SKLWriteResGroups = []
    instructions = []

    for SKLWriteResGroup in sKLWriteResGroupDef.searchString(open('X86SchedSkylakeClient.td').read()):
        SKLWriteResGroups.append(SKLWriteResGroup.asDict())

    for instrGroup in instrGroupDef.searchString(open('X86SchedSkylakeClient.td').read()):
        instructions.append(instrGroup.asDict())


    #Extract all regex
    regexList = []
    for instruction in instructions:
        regexList.append(instruction['Regex'])

    # print(regexList)

    #Match instructions and regex
    matchings = instructionMatching(uniInstr, regexList)
    print("Matchings:")
    print(matchings['Matched'])

    print("Unmatched instructions:")
    print(matchings['Unmatched'])


#Find out if there are any instructions not matched to the instructions defined in unison
def instructionMatching (instructions, regexList):
    matchings = {
            'Matched' :  [],
            'Unmatched' : []
            }

    for instruction in instructions:
        matched = False
        for regex in regexList:
            #If we find a matching, we should move onto the next instruction
            if matched:
                continue;

            searchResult = re.search(regex, instruction) 

            if searchResult is not None:
                matching = {
                        'Instruction' : instruction,
                        'Regex' : regex
                        }

                matched = True
                matchings['Matched'].append(matching)

        if not matched:
            matchings['Unmatched'].append(instruction)

    return matchings

if __name__ == '__main__':
    main()

