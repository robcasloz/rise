#!/usr/bin/env python

import json

input = json.load(open("output/X86SchedSkylakeClient-parser_output.json"))

print "---"
print "instruction-set:"
print ""
print "  - group: ITINERARIES"
print "    instructions:"
print ""

for instruction in input["DefinedInstructions"]:
    print ("        - id:        " + instruction["Instruction"])
    print ("          itinerary: " + instruction["ResourceGroup"])
    print ""
