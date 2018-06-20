#!/usr/bin/env python

import yaml
import pyparsing as pp
import re
import time

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

    # print(yaml.dump(SKLWriteResGroups, default_flow_style=False))
    # print(yaml.dump(instructions, default_flow_style=False))

    #Extract all regex
    regexList = []
    for instruction in instructions:
        regexList.append(instruction['Regex'])

    # print(regexList)

    # Match instructions and regex
    matchings = instructionMatching(uniInstr, regexList)
    print("Matchings:")
    print(yaml.dump(matchings['Matched'], default_flow_style=False))

    print("Unmatched instructions:")
    print(yaml.dump(matchings['Unmatched'], default_flow_style=False))

    print("Sizes:")
    print("matched: " + str(len(matchings['Matched'])))
    print("unmatched: " + str(len(matchings['Unmatched'])))
    print("Total should be: " + str(len(uniInstr)))


#Find out if there are any instructions not matched to the instructions defined in unison, this function is slow (O(n^2)) due to testing all combinations of both input lists, so alot of things are aimed at improving its speed
def instructionMatching (instructions, regexList):
    #Dictionary to save results
    matchings = {
            'Matched' :  [],
            'Unmatched' : []
            }

    alNumRegex = []
    noAlNumRegex = []
    #Divide regex'es into those with just alphanumericals, as they dont contain any special rules and we can just perform regular string-matching
    for regex in regexList:
        if regex.isalnum():
            alNumRegex.append(regex)
        else:
            noAlNumRegex.append(regex)

    tempUnmatched = []
    #See if we get an instant match before trying expensive regex
    for instruction in instructions:
        if instruction in set(alNumRegex):
            matching = {
                'Instruction' : instruction,
                'Regex' : instruction
            }
            matchings['Matched'].append(matching)

        else:
            tempUnmatched.append(instruction)

    #Perform more expensive regex matching for instructions not found through string-matching
    for instruction in tempUnmatched:
        matched = False
        for regex in noAlNumRegex:
            #Check if we already matched the instruction with an earlier regex
            if matched:
                continue;

            searchResult = re.search(regex, instruction) 
            #Check if we matched the whole instruction
            if (not (searchResult is None) and searchResult.end() - searchResult.start() == len(instruction)):
                matching = {
                    'Instruction' : instruction,
                    'Regex' : regex
                }
                matchings['Matched'].append(matching)
                matched = True
        
        if not matched:
            #Instruction wasnt matched with any regex
            matchings['Unmatched'].append({'Instruction' : instruction})

    return matchings

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))

