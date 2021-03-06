#!/usr/bin/env python

import json

input = json.load(open("output/X86SchedSkylakeClient-parser_output.json"))

excluded = ["SchedRW", "SchedRW.Folded", "SKLPort0156", "SKLPort15", "SKLPort23", "SKLPort4", "SKLWriteResGroup1", "SKLWriteResGroup112", "SKLWriteResGroup113", "SKLWriteResGroup162", "SKLWriteResGroup169", "SKLWriteResGroup171", "SKLWriteResGroup180", "SKLWriteResGroup196", "SKLWriteResGroup2", "SKLWriteResGroup202", "SKLWriteResGroup206", "SKLWriteResGroup208", "SKLWriteResGroup215", "SKLWriteResGroup220", "SKLWriteResGroup32", "SKLWriteResGroup35", "SKLWriteResGroup37", "SKLWriteResGroup39", "SKLWriteResGroup53", "SKLWriteResGroup54", "SKLWriteResGroup68", "SKLWriteResGroup69", "SKLWriteResGroup73", "SKLWriteResGroup78", "SKLWriteResGroup92", "WriteAESDecEnc", "WriteAESDecEncLd", "WriteAESIMC", "WriteAESIMCLd", "WriteAESKeyGen", "WriteAESKeyGenLd", "WriteBlend", "WriteBlendLd", "WriteCLMul", "WriteCLMulLd", "WriteCvtF2F", "WriteCvtF2I", "WriteCvtI2F", "WriteFBlend", "WriteFBlendLd", "WriteFence", "WriteFHAdd", "WriteFHAddLd", "WriteFRcp", "WriteFRsqrt", "WriteFShuffle256", "WriteFShuffle256Ld", "WriteFSqrt", "WriteFVarBlend", "WriteFVarBlendLd", "WriteIMulH", "WriteLEA", "WriteMPSAD", "WriteMPSADLd", "WritePCmpEStrI", "WritePCmpEStrILd", "WritePCmpEStrM", "WritePCmpEStrMLd", "WritePCmpIStrI", "WritePCmpIStrILd", "WritePCmpIStrM", "WritePCmpIStrMLd", "WriteShift", "WriteShiftLd", "WriteShuffle", "WriteShuffle256", "WriteShuffle256Ld", "WriteShuffleLd", "WriteVecLogicLd", "WriteVecLogicLd", "WriteVarBlendLd", "WriteVarBlend"]

property_list = []
for properties in input["ResourceGroups"]:
    resources = []
    for (res, c) in zip(properties["Resources"], properties["ResourceCycles"]):
        resources.append("(" + res + ", " + str(c) + ")")
    it = properties["Name"]
    if not (it in excluded):
        property_list.append("(" + it + \
                             ", (" + str(properties["Latency"]) + \
                             ", [" + ', '.join(resources) + "]))")

print "-- This file has been generated by the 'produce-itinerary-properties' script. Do not modify by hand!"
print ""
print "module Unison.Target.X86.SpecsGen.ItineraryProperties (itineraryProperties) where"
print ""
print "import qualified Data.Map as M"
print "import Unison.Target.X86.X86ResourceDecl"
print "import Unison.Target.X86.SpecsGen.X86ItineraryDecl"
print ""
print "itineraryProperties = M.fromList";
print " [" + ",\n  ".join(property_list) + "]"
