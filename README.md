# Unison x86 resource model
Introduction
============
Work done by Jacob Kimblad during his time as a student intern on the Unison compiler reasearch project. The goal was to produce a valid resource model for X86-architectures used by Unison during instruction selection and instruction scheduling.

Resource model based on the works of Agner Fog
==============================================
Agner Fog has compiled a bunch of information about the resource usage of x86 instructions for a load of different architectures. The information is compiled in tabels which are available at his personal website here.There are located at his personal website [here](http://www.agner.org/optimize/) ("Instruction tables: Lists of instruction latencies, throughputs and micro-operation breakdowns for Intel, AMD and VIA CPUs"). 
Currently, this covers only about ~500 instructions, and it is unclear wether or not this number will increase or not, depending on if Agner will update the tables.
<http://www.agner.org/optimize/> located in optimization manual 4.

### Calculations
A disadvantage of this model is that there is no information about how long individual processor resources are used for, as the throughput is defined on instruction level, and not on µ-operation level. This can be improved a bit for operations using the load/store resources, and is explained in detail under "Load/Store-ports".

#### Throughput
The amount of time a resource is held is calculated by the following equation

resource usage = reciprocal ``throughput`` * (cardinality / prefix)

#### Load/Store-ports
Resources "p23", "p237" and "p4" are used for making loads and stores. 

Results
-------
The results are gathered in /agner-fog-resource-model/output/agner-resource-model_output.json

Generating the results
----------------------

### agner-resource-model_output.json
The output is formatted as a JSON dictionary with the following hierarchy. Most of the information is redundant and is kept as-is from the original table.
	
	{
	    "ResourceUsage": [
	        {
	            "Instruction": "MOV",
	            "Operands": "r,i",
	            "Resources": [
	                {
	                    "Resource": "p0156",
	                    "ResourceUsage": 1,
	                    "HoldTime": 1.0
	                }
	            ]
	        }
	    ]
	    "UndefinedPorts": [
	        {
	            "Instruction": "RCR RCL",
	            "Operands": "m,i",
	            "Uops fused domain": 11,
	            "Uops unfused domain": 11,
	            "Uops each port": null,
	            "Latency": null,
	            "Reciprocal throughput": 6,
	            "Comments": null
	        },
	    ]
	    "NoReciprocalThrougput": [
	        {
	            "Instruction": "CWDE",
	            "Operands": null,
	            "Uops fused domain": 1,
	            "Uops unfused domain": 1,
	            "Uops each port": "p0156",
	            "Latency": 1,
	            "Reciprocal throughput": null,
	            "Comments": null
	        },
	    ]
	    "UndefinedReciprocalThrougput": [
	        {
	            "Instruction": "MOVBE",
	            "Operands": "r16,m16",
	            "Uops fused domain": 3,
	            "Uops unfused domain": 3,
	            "Uops each port": "2p0156 p23",
	            "Latency": null,
	            "Reciprocal throughput": "0.5-1",
	            "Comments": "MOVBE"
	        },
	    ]
	}


* ResourceUsage are instructions that are complete with all definintons of their resource usage.
* UndefinedPorts are instructions that have no ports defined, but they do however have a reciprocal throughput defined. These would be modeled as taking zero resources.
* NoReciprocalThroughput are instructions that have no reciprocal throughput defined. These would be modeled as holding their resources for zero cycles.
* UndefinedReciprocalThroughput are instructions that have a defined reciprocal throughput that is non-numerical. A lot of these can easily be solved manually or automatically as it typically is a question of the throughput being defined on an interval, or an estimation, examples : "0.5-2", "~200".


### Coverage
There are 354 instructions defined in the ResourceUsage list in "agner-resource-model_output.json". It is unclear how many of these that are used in Unison, as work still remains to be done in mapping these instructions to their representatives in LLVM.

Resource model based on LLVM 6.0.0
==================================
This resource model is currently based on the llvm 6.0.0 resource model for the Intel Skylake processor (6th generation). The primary file used from llvm is  llvm/lib/Target/X86/X86SchedSkylakeClient.td which contains the majority of information needed.

Introduction
------------
Each instruction is mapped to a "ResourceGroup" which can be thought of as an itinerary. Several instructions can share the same resource group, and the resource group holds information about the instructions resource usage. Each resource group contains the following information:

* Latency
* Resources
* ResourceCycles

Latency defines the duration between issuing the instruction until when its results are ready for use. 
Resources and ResourceCycles are lists of equal size, where Resources is a list of strings that defines resources, and ResourceCycles is a list of integers that define how many cycles each corresponding resource is used for.

It is worth noting that LLVM gets ResourceCycles from how many µ-ops are issued onto each resource for the given instruction. This assumes that we can issue one µ-op into a given port (resource) each cycle, which in reality is not true. This is a flaw in the LLVM resource model, it is most likely due to the difficulties of getting more precise information about the x86-architecture.

Mapping instructions to resource-groups
---------------------------------------
Instructions are mapped to resource-groups using two different methods that follow bellow. Instructions primarily get their assigned resource group by using the first method. Since the first method does not cover all instructions, the second method is used to cover additional instructions.

### Using regular expression
The first way is that the file "X86SchedSkylakeClient.td" defines a lot of regular expressions that each represent a single, or several instructions. Each regular expression is then mapped to a resource group in the same file, meaning that every instruction matching that specific regular expression is part of the same resource group.
Example: 

	def: InstRW<[SKLWriteResGroup10], (instregex "ADD(16|32|64)ri")>;
Maps all instructions matching the regular expression "ADD(16|32|64)ri" to the resource group SKLWriteResGroup10.

### Using TableGen
The second is that LLVM's tablegen command can output information about all isntructions defined for the x86 architecture. Part of this information is  a list of resource groups, which define what particular resource groups that instruction is part of. The reason for it being a list is that depending on what x86-architecture the code is being compiled for, different resource groups are used(for example, there is a difference between AMD and Intel architectures).
Example:
ADD16ri defines:

	list<SchedReadWrite> SchedRW = [WriteALU];

Where WriteALU is a resource group defined in "X86SchedSkylakeClient.td".

Additional LLVM resource modelling
----------------------------------
There is a resource defining for how long the load register can be used before it needs to be available to receive the load after the original instruction was issued.

	// Loads are 5 cycles, so ReadAfterLd registers needn't be available until 5
	// cycles after the memory operand.
	def : ReadAdvance<ReadAfterLd, 5>;


Results
-------
The results are located in the file /llvm-resource-model/output/X86SchedSkylakeClient-parse_output.json

### X86SchedSkylakeClient-parse_output.json
The JSON is constructed as follows:

	{
	    "ResourceGroups": [
	        {
	            "Name": "WriteALU",
	            "Latency": 1,
	            "Resources": [
	                "SKLPort0156"
	            ],
	            "ResourceCycles": [
	                1
	            ]
	        } 
	    ],
	    "DefinedInstructions": [
	        {
	            "Instruction": "ADC8i8",
	            "ResourceGroup": "SKLWriteResGroup23"
	        }
	    ],
	    "UndefinedInstructions": [
	        {
	            "Instruction": "BUNDLE"
	        }
	    ]
	}



* "ResourceGroups" holds a list of dictionaries, containing all the resource groups which are defined
	* "Name" is a string of the llvm-corresponding name of the resource group.
	* "Latency" is an integer representing the delay that the instruction generates in a dependency chain.
	* "Resources" is a list of strings, representing what specific resources are used by an instruction.
	* "ResourceCycles" is a list of integers where each integer represents for how many cycles a resource is kept by an instruction.
* "DefinedInstructions" holds a list of all the instructions which are mapped to a resource-group
* "UndefinedInstructions" holds a list of all the instruction which are NOT currently mapped to any resource-group


### Coverage
As of writing (2018-07-20), this resource model currently covers 3613/4292 instructions located at /unison/src/unison/src/Unison/Target/X86/SpecsGen/AllInstructions.hs in Unison.

Generating the results
----------------------
There are a set of tools that automatically create the resource specification from LLVM resources.

Currently, the information is extracted from LLVM 6.0.0

The folder "llvm-resource-model" contains all the tools to pull the necessary information from LLVM's resource model (See "Resource model based on LLVM's resource model").

### unison_instructions.py
Contains function to return all instructions defined in Unison for X86 as a python list object.

### tablegen-instruction-parser.py
Input: The output from llvms tablegen as stdin, tablegen should be invoked as follows:
llvm-tblgen /.../llvm-6.0.0.src/lib/Target/X86/X86.td -InstrInfo -I /.../llvm-6.0.0.src/include -I /.../llvm-6.0.0.src/lib/Target/X86
Where the the llvm-6.0.0 is the source code folders (non-compiled) for llvm 6.0.0
Output: A list of all instructions with a respective SchedRW defined. This is used to map the instruction to its specific resource-group, if it wasn't done using the regular expressions.

### X86SchedSkylakeClient-parser.py
Input: The file "X86SchedSkylakeClient.td" from the input-folder. Also the output of tablegen-instruction-parser.py, currently fetched from "tablegen-instruction-parser_output.td" in the input folder.
Output: See heading "X86SchedSkylakeClient-parse_ouput.json"

