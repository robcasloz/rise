#!/usr/bin/env python

import yaml
import json
import pyparsing as pp
import re
import time
import ast
import sys

#Separate file with a list containing all x86 instructions defined for unison
from unison_instructions import getUnisonInstructions

def main():

    #Get all instructions defined in unison
    unisonInstructions = getUnisonInstructions()

    #Parser to find each basic WriteRes def with no additional attributes
    writeResDefParser = getWriteResDefParser()
    #Parser to find each WriteRes def with additional attributes (latency, resourcecycles etc.)
    writeResVerboseDefParser = getWriteResVerboseDef()
    #Parser to find each SKLWriteResPair def
    sklWriteResPairDefParser = getSklWruteResPairDefParser()
    #Parser to find each regex-instructions that belongs to a SKLWriteResGroup
    llvmInstructionParser = getLlvmInstructionParser()
    #Parser to find each SKLWriteResGroup definition
    sklWriteResGroupDefParser = getSklWriteResGroupDefParser()

    #Open LLVM-tablegen file defining skylake resources
    schedSkylakeClientTD = open('X86SchedSkylakeClient.td').read()

    #Find all WriteRes defs
    writeResDefs = getWriteResDefs(writeResDefParser, schedSkylakeClientTD)
    #Find all verbose WriteRes defs
    writeResVerboseDefs = getWriteResVerboseDefs(writeResVerboseDefParser, schedSkylakeClientTD)
    #Find all SKLWriteResPair defs
    sklWriteResPairDefs = getSklWriteResPairDefs(sklWriteResPairDefParser, schedSkylakeClientTD)
    #Find all SKLWriteResGroup defs
    sklWriteResGroupDefs = getSklWriteResGroupDefs(sklWriteResGroupDefParser, schedSkylakeClientTD)
    #Find all instructions defined for skylake by llvm
    llvmInstructions = getLlvmInstructions(llvmInstructionParser, schedSkylakeClientTD)

    # Find out which unison instructions has a matching regular-expression defined in llvm .td
    matchings = regexMatching(unisonInstructions, llvmInstructions)

    #Open file that contains output from tablegen
    instructionRWSchedGroupTuples = json.load(open('tablegenOutput-parsed.json'))
    # Try and match all remaining instructions, that are not matched with any resource group, with what their schedRWGroups are defined as from the output of tablegen
    schedRWMatchings = getSchedRWMatchings(matchings['Unmatched'], instructionRWSchedGroupTuples)
        
    #Save all defined resource groups
    resourceGroups = []
    for group in writeResDefs + writeResVerboseDefs + sklWriteResPairDefs:
        resourceGroups.append(group['Name'])

    #Remove undefined resourcegroups from each defined instruction
    undefinedSchedRWGroup = []
    for instruction in list(schedRWMatchings['Matched']):
        tempInstruction = removeUndefinedResourceGroups(instruction, resourceGroups)
        #Instruction had no defined resource group for skylake, so its resource usage is unedfined
        if not tempInstruction['ResourceGroup']:
            undefinedSchedRWGroup.append({'Instruction': tempInstruction['Instruction']})
            schedRWMatchings['Matched'].remove(instruction)
        else:
            instruction = tempInstruction

    #Format the output and print json (indent=4 enables pretty print)
    output = {
            'ResourceGroups': sklWriteResGroupDefs + writeResVerboseDefs + writeResDefs,
            'DefinedInstructions': matchings['Matched'] + schedRWMatchings['Matched'],
            'UndefinedInstructions': schedRWMatchings['Unmatched'] + undefinedSchedRWGroup,
            }
    print(json.dumps(output, indent=4))

    # Uncomment to print number of instructions NOT mapped to a resource group
    # print("unmatched: " + str(len(output['UndefinedInstructions'])))
    # Uncomment to print number of instructions mapped to a resource group
    # print("matched" + str(len(output['DefinedInstructions'])))

#Removes undefined resouorcegroups from an instruction
def removeUndefinedResourceGroups (instruction, resourceGroups):
    #Get resource groups that are part of the ones defined for skylake AND are part of the instruction
    undef = list(set(instruction['ResourceGroup']) - set(resourceGroups))
    instruction['ResourceGroup'] = "".join(list(set(resourceGroups).intersection(set(instruction['ResourceGroup']))))
    # instruction['ResourceGroup'] = "".join(tempInst)
    return instruction

#Parser to find each basic WriteRes def with no additional attributes
def getWriteResDefParser():
    return pp.Suppress("def : WriteRes<") + pp.SkipTo(",")("Name")  + pp.SkipTo(">")("Resources") + pp.Suppress(">") + ~pp.Suppress("{") 

#Parser to find each WriteRes def with additional attributes (latency, resourcecycles etc.)
def getWriteResVerboseDef():
    return pp.Suppress("def : WriteRes<") + pp.SkipTo(",")("Name")  + pp.SkipTo(">")("Resources") + pp.Suppress(">") + pp.Suppress("{")  + pp.SkipTo("}")("Data") + pp.Suppress("}")

#Parser to find each SKLWriteResPair def
def getSklWruteResPairDefParser():
    return pp.Suppress("defm : SKLWriteResPair<") + pp.SkipTo(",")("Name") + pp.Suppress(",") +  pp.SkipTo(",")("Resources") + pp.Suppress(",") + pp.SkipTo(">")("Latency")

#Parser to find each regex-instructions that belongs to a SKLWriteResGroup
def getLlvmInstructionParser():
    writeResGroup = pp.Word(pp.alphanums)
    instRegex = pp.SkipTo("\"")
    return pp.Suppress("def: InstRW<[") + writeResGroup("ResourceGroup") + pp.Suppress("], (instregex \"") + instRegex("Regex") + pp.Suppress("\")>;")
    
#Parser to find each SKLWriteResGroup definition
def getSklWriteResGroupDefParser():
    writeResGroup = pp.Word(pp.alphanums)
    resources = pp.SkipTo("]")
    latency = pp.Word(pp.nums)
    microOps = pp.Word(pp.nums)
    resourceCycles = pp.SkipTo("]")
    return pp.Suppress("def ") + writeResGroup("SKLWriteResGroup") + pp.Suppress(": SchedWriteRes<[") + resources("Resources") + pp.Suppress(pp.restOfLine) + (
            pp.Suppress("let Latency = ") + latency("Latency")  + pp.Suppress(pp.restOfLine) +
            pp.Suppress("let NumMicroOps = ") + microOps("NumMicroOps") + pp.Suppress(pp.restOfLine) + 
            pp.Suppress("let ResourceCycles = [") + resourceCycles("ResourceCycles") + pp.Suppress(pp.restOfLine)
        )

#Find all WriteRes defs
def getWriteResDefs(writeResDef, schedSkylakeClientTD):
    writeResDefs = []
    for writeRes in writeResDef.searchString(schedSkylakeClientTD):
        #Pretty up the parsed data
        tempDict = {
                "Name": writeRes['Name'],
                "Latency": None,
                "Resources": writeRes['Resources'].strip(",").strip().strip("[").strip("]").replace(" ", "").split(","),
                "ResourceCycles": [],
                }
        writeResDefs.append(tempDict)
    return writeResDefs

#Find all verbose WriteRes defs
def getWriteResVerboseDefs(writeResVerboseDef, schedSkylakeClientTD):
    writeResVerboseDefs = []
    for writeRes in writeResVerboseDef.searchString(schedSkylakeClientTD):
        #Pretty up the parsed data
        writeResDict = writeRes.asDict()
        tempDict = {
                'Name' : writeRes['Name'],
                'Latency' : None,
                'Resources' : writeRes['Resources'].strip(",").strip().strip("[").strip("]").replace(" ", "").split(","),
                'ResourceCycles' : []
                }
        
        #Go through each line of data that belongs to the WriteRes
        tempData = writeResDict['Data'].strip().split("\n")
        for data in tempData:
            #Remove comments that may have been parsed
            data = data.split("//")[0]
            if data:
                data = data.strip(";").strip()
                if data.find("Latency") >= 0 :
                    #Latency is not an int
                    if isNumber(data.split("=")[1].strip()):
                        tempDict['Latency'] = int(data.split("=")[1].strip())
                    #Latency is NaN (This happens due to wrongfully parsing once inside a specially defined function)
                    else:
                        tempDict['Latency'] = None
                elif data.find("ResourceCycles") >= 0:
                    tempData = data.split("=")[1].strip().replace(" ", "").strip("[").strip("]").split(",")
                    #Check all list items are numericals
                    tempIntData = [s for s in tempData if s.isdigit()]
                    tempDict['ResourceCycles'] = list(map(int, tempIntData))

        writeResVerboseDefs.append(tempDict)
        
    return writeResVerboseDefs

#Find all SKLWriteResPair defs
def getSklWriteResPairDefs(sklWriteResPairDef, schedSkylakeClientTD):
    sklWriteResPairs = []
    for sklWriteResPair in sklWriteResPairDef.searchString(schedSkylakeClientTD):
        tempDict = {
                'Name' : sklWriteResPair['Name'],
                'Latency' : int(sklWriteResPair['Latency']),
                'Resources' : sklWriteResPair["Resources"].strip(",").strip().split(","),
                #RecourceCycles is undefined for the current version of the .td file, but ought probably be updated if the file is changed to a later version of llvm than 6.0.0
                'ResourceCycles' : []
                }
        sklWriteResPairs.append(tempDict)

    return sklWriteResPairs

#Find all SKLWriteResGroup defs
def getSklWriteResGroupDefs(sklWriteResGroupDef, schedSkylakeClientTD):
    sklWriteResGroupDefs = []
    for sklWriteResGroup in sklWriteResGroupDef.searchString(schedSkylakeClientTD):
        tempDict = {
                'Name' : sklWriteResGroup['SKLWriteResGroup'],
                'Latency' : int(sklWriteResGroup['Latency']),
                'Resources' : sklWriteResGroup['Resources'].strip(",").strip().split(","),
                'ResourceCycles' : list(map(int, sklWriteResGroup['ResourceCycles'].split(",")))
                }
        sklWriteResGroupDefs.append(tempDict)
    return sklWriteResGroupDefs

#Find all instructions defined for skylake by llvm
def getLlvmInstructions(instrGroupDef, schedSkylakeClientTD):
    instructions = [] 
    for instrGroup in instrGroupDef.searchString(schedSkylakeClientTD):
        instructions.append(instrGroup.asDict())
    return instructions
    #InstrGroup.asDict() returns the following data structure
        # dict = {
                # SKLWriteResGroup
                # instRegex
                # }

#Check if parameter is a number
def isNumber(a):
    try:
        int(a)
        return True
    except ValueError:
        return False

#Get the SchedRW groups that belongs to each instruction passed as argument
def getSchedRWMatchings(instructions, instructionRWSchedGroupTuples):

    matches = {
            'Matched': [],
            'Unmatched': []
            }

    for data in instructions:
        instruction = data['Instruction']
        match = list(filter(lambda schedRW : schedRW['Instruction'] == instruction, instructionRWSchedGroupTuples))
        if match and match[0]['SchedRW'] != '?':
            matching = {
                    'Instruction': instruction,
                    'ResourceGroup': match[0]['SchedRW'].strip("[").strip("]").replace(" ", "").split(",")
                    }
            matches['Matched'].append(matching)

        else:
            matches['Unmatched'].append(data)

    return matches

#Find out if there are any instructions not matched to the instructions defined in unison, this function is slow due to testing all combinations of both input lists, so alot of things are aimed at improving its speed
def regexMatching (unisonInstructions, instructions):
    #Dictionary to save results
    matchings = {
            'Matched' :  [],
            'Unmatched' : []
            }

    alNumRegex = []
    notAlNumRegex = []
    #Divide regex'es into those with just alphanumericals, as they dont contain any special rules and we can just perform regular string-matching
    for instruction in instructions:
        #TODO: Allow instruction to contain "_" as well as alphanumericals for speed improvements
        if instruction['Regex'].isalnum():
            alNumRegex.append(instruction)
        else:
            notAlNumRegex.append(instruction)

    tempUnmatched = []
    #See if we get a string match before trying expensive regex
    for unisonInstruction in unisonInstructions:
        # Match possible unison instructions with llvm-regex(containing only alphanumericals) by checking string equality
        match = list(filter(lambda alNum : alNum['Regex'] == unisonInstruction, alNumRegex))
        # Unison-instruction matched a llvm-regex
        if match:
            matching = {
                    'Instruction' : unisonInstruction,
                    'ResourceGroup' : match[0]['ResourceGroup'],
                    }
            matchings['Matched'].append(matching)

        else:
            tempUnmatched.append(unisonInstruction)

    #Perform more expensive regex matching for instructions not found through string-matching
    for instruction in tempUnmatched:
        matched = False
        for regex in notAlNumRegex:
            #Check if we already matched the instruction with an earlier regex
            if matched:
                continue;

            searchResult = re.search(regex['Regex'], instruction) 
            #Check if we matched the whole instruction
            if (not (searchResult is None) and searchResult.end() - searchResult.start() == len(instruction)):
                matching = {
                        'Instruction' : instruction,
                        'ResourceGroup' : regex['ResourceGroup'],
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

