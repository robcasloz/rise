#!/usr/bin/env python

import yaml
import pyparsing as pp

#Separate file with a list containing all x86 instructions defined for unison
from unison_instructions import unisonInstructions

#Transform string of unison instructions to a list of strings with individual instructions
instructions = unisonInstructions.replace("\n", '')
instructions = instructions.replace("\t", '')
instructions = instructions.replace(" ", '')
instructions = instructions.split(",")
print (instructions)

writeResGroup = pp.Word(pp.alphanums)
instRegex = pp.SkipTo("\"")

#Parser to find each regex-instructions that belongs to a SKLWriteResGroup
instrGroupDef = pp.Suppress("def: InstRW<[") + writeResGroup("SKLWriteResGroup") + pp.Suppress("], (instregex \"") + instRegex("Regex") + pp.Suppress("\")>;")

ports = pp.SkipTo("]")
latency = pp.Word(pp.nums)
microOps = pp.Word(pp.nums)
resourceCycles = pp.SkipTo("]")
# lineEnd = pp.Suppress(pp.LineEnd)
#Parser to find each SKLWriteResGroup definition
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

# print (unison_instructions)
# print ("Skylake WriteResGroups: ")
# print (yaml.dump(SKLWriteResGroups, default_flow_style = False))
# print ("Skylake instructions: ")
# print (yaml.dump(instructions, default_flow_style = False))

