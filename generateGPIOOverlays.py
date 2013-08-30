# Generates device tree overlays for runtime config of every gpio pin.
# 	creates dts files, compile script, and install script
#
# Usage:
#   python generateGPIOOverlays.py	# generates the dts files in the dts directory.
#	cd generated
#   sh compile.sh
#   sh install.sh
# 
# Set P9.11 to gpio, RX enabled, pull up
#	echo gpio-P9.11 > /sys/devices/bone_capemgr.*/slots

import itertools
import operator 
import templates

gpioPins = [
	# format is ( header name, hard ip name, offset , kernel number, mux mode for gpio)
	# put together from the list at https://docs.google.com/spreadsheet/ccc?key=0As0aJokrBccAdEdwNmVQdHhSd0dmSWZMaWdJbVZJMkE&hl=en#gid=2
	( "P8.3", "gpio1_6", 0x18, 6, 7 ),
	( "P8.4", "gpio1_7", 0x1C, 7, 7 ),
	( "P8.5", "gpio1_2", 0x08, 2, 7 ),
	( "P8.6", "gpio1_3", 0x0C, 3, 7 ),
	( "P8.7", "gpio2_2", 0x90, 36, 7 ),
	( "P8.8", "gpio2_3", 0x94, 37, 7 ),
	( "P8.9", "gpio2_5", 0x9C, 39, 7 ),
	( "P8.10", "gpio2_4", 0x98, 38, 7 ),
	( "P8.11", "gpio1_13", 0x34, 13, 7 ),
	( "P8.12", "gpio1_12", 0x30, 12, 7 ),
	( "P8.13", "gpio0_23", 0x24, 9, 7 ),
	( "P8.14", "gpio0_26", 0x28, 10, 7 ),
	( "P8.15", "gpio1_15", 0x3C, 15, 7 ),
	( "P8.16", "gpio1_14", 0x38, 14, 7 ),
	( "P8.17", "gpio0_27", 0x2C, 11, 7 ),
	( "P8.18", "gpio2_1", 0x8C, 35, 7 ),
	( "P8.19", "gpio0_22", 0x20, 8, 7 ),
	( "P8.20", "gpio1_31", 0x84, 33, 7 ),
	( "P8.21", "gpio1_30", 0x80, 32, 7 ),
	( "P8.22", "gpio1_5", 0x14, 5, 7 ),
	( "P8.23", "gpio1_4", 0x10, 4, 7 ),
	( "P8.24", "gpio1_1", 0x04, 1, 7 ),
	( "P8.25", "gpio1_0", 0x00, 0, 7 ),
	( "P8.26", "gpio1_29", 0x7C, 31, 7 ),
	( "P8.27", "gpio2_22", 0xE0, 56, 7 ),
	( "P8.28", "gpio2_24", 0xE8, 58, 7 ),
	( "P8.29", "gpio2_23", 0xE4, 57, 7 ),
	( "P8.30", "gpio2_25", 0xEC, 59, 7 ),
	( "P8.31", "gpio0_10", 0xD8, 54, 7 ),
	( "P8.32", "gpio0_11", 0xDC, 55, 7 ),
	( "P8.33", "gpio0_9", 0xD4, 53, 7 ),
	( "P8.34", "gpio2_17", 0xCC, 51, 7 ),
	( "P8.35", "gpio0_8", 0xD0, 52, 7 ),
	( "P8.36", "gpio2_16", 0xC8, 50, 7 ),
	( "P8.37", "gpio2_14", 0xC0, 48, 7 ),
	( "P8.38", "gpio2_15", 0xC4, 49, 7 ),
	( "P8.39", "gpio2_12", 0xB8, 46, 7 ),
	( "P8.40", "gpio2_13", 0xBC, 47, 7 ),
	( "P8.41", "gpio2_10", 0xB0, 44, 7 ),
	( "P8.42", "gpio2_11", 0xB4, 45, 7 ),
	( "P8.43", "gpio2_8", 0xA8, 42, 7 ),
	( "P8.44", "gpio2_9", 0xAC, 43, 7 ),
	( "P8.45", "gpio2_6", 0xA0, 40, 7 ),
	( "P8.46", "gpio2_7", 0xA4, 41, 7 ),
	( "P9.11", "gpio0_30", 0x70, 28, 7 ),
	( "P9.12", "gpio1_28", 0x78, 30, 7 ),
	( "P9.13", "gpio0_31", 0x74, 29, 7 ),
	( "P9.15", "gpio1_16", 0x40, 16, 7 ),
	( "P9.17", "gpio0_4", 0x5C, 87, 7 ),
	( "P9.18", "gpio0_5", 0x58, 86, 7 ),
	( "P9.19", "gpio0_13", 0x7C, 95, 7 ),
	( "P9.20", "gpio0_12", 0x78, 94, 7 ),
	( "P9.21", "gpio0_3", 0x54, 85, 7 ),
	( "P9.22", "gpio0_2", 0x50, 84, 7 ),
	( "P9.23", "gpio1_17", 0x44, 17, 7 ),
	( "P9.24", "gpio0_15", 0x84, 97, 7 ),
	( "P9.25", "gpio3_21", 0xAC, 107, 7 ),
	( "P9.26", "gpio0_14", 0x80, 96, 7 ),
	( "P9.27", "gpio3_29", 0xA4, 105, 7 ),
	( "P9.28", "gpio3_17", 0x9C, 103, 7 ),
	( "P9.29", "gpio3_15", 0x94, 101, 7 ),
	( "P9.30", "gpio3_16", 0x98, 102, 7 ),
	( "P9.31", "gpio3_14", 0x90, 100, 7 )
]

def getCombinations(stateList):
	states = [list(reversed(state)) for state in stateList]	# reverse them all so they come out in order
	stateLengths = [len(state) - 1 for state in states]
	cycles = [itertools.cycle(state) for state in states]
	count = [length for length in stateLengths]
	indexes = list(range(len(states)))
	working = True
	while working:
		combinations = [states[i][count[i]] for i in indexes]
		for stateIndex in indexes:
			if count[stateIndex] == 0:
				continue
			else:
				count[stateIndex] -= 1
				if stateIndex:
					count[:stateIndex] = stateLengths[:stateIndex]	# reset all the lower counters
				break
		else:
			# all counts zero, so all done.
			working = False
		yield combinations

def generateDTSFiles(gpioPins, states):
	# create all of the dts files for each pin. include all of the states.
	# returns the list of filenames created
	dtsFilenames = []
	for pin in gpioPins:
		headerName, hardwareName, offset, kernelPin, gpioMuxMode = pin

		partNumber = "gpio-%s" % headerName
		version = "00A0"
		filename = "%s-%s" % (partNumber, version)
		
		values = {										# template values related to this pin
			"header name": headerName,
			"clean header name": headerName.replace(".","_"),
			"gpio offset": hex(offset),
			"version": version,
			"part number": partNumber,
			"header names": '"%s"' % headerName,       	# put quotes around it
			"hardware names": '"%s"' % hardwareName,   	# put quotes around it
		}
		
		fragmentList = []								# list of all the processed fragment templates
		pinctrlList = []								# list of all the processed pinctrl templates
		
		## fill out all of the fragment and pinctrl templates
		index = 0
		for stateName, stateMuxBits in states:
			stateValues = {		# template values related to this state
				"index": index,
				"state name": stateName,
				"mux mode": hex(gpioMuxMode | stateMuxBits )
			}
			values.update(stateValues)
			
			fragmentList.append(templates.populate(templates.fragment, values))		# make a fragment for these state values
			pinctrlList.append(templates.populate(templates.pinctrl, values))		# make pinctrl entry for these state values
			
			index += 1
		
		# last fragment entry for pinmux helper
		helperValues =	{
			"index": index, # last fragment
			"state names list": ", ".join(['"%s"' % stateName for stateName, stateMuxBits in states]),
			"pinctrl list": "\n\t\t\t\t".join(pinctrlList),
		}
		values.update(helperValues)
		fragmentList.append(templates.populate(templates.pinmuxHelper, values))

		## dts template
		dtsValues = {
			"fragments": "".join(fragmentList)
		}
		values.update(dtsValues)
		dtsFileContents = templates.populate(templates.dtsContents, values)
		
		## write the dts file for this pin!
		print "Writing", filename
		f = open("%s.dts" % filename, "w")
		try:
			f.write(dtsFileContents)
		finally:
			f.close()
			
		dtsFilenames.append(filename)
	return dtsFilenames

def generateCompileScript(dtsFilenames):
	print "Generating compile script."
	f = open("compile.sh", "w")
	try:
		f.write("echo Compiling dts files...\n")
		command = "echo \ \ %s.dts -\> %s.dtbo\ndtc -O dtb -o %s.dtbo -b 0 -@ -I dts %s.dts\n"
		for filename in dtsFilenames:
			f.write(command % (filename, filename, filename, filename))
		f.write("echo Done.")
	finally:
		f.close()
	print "Done."	
	
def generateInstallScript(dtsFilenames):
	print "Generating install script."
	f = open("install.sh", "w")
	f.write("echo Installing dtbo files to /lib/firmware...\n")
	command = "cp %s.dtbo /lib/firmware\n"
	for filename in dtsFilenames:
		f.write(command % (filename))
	f.write("echo Done.\n")	
	f.close()
	print "Done."
	
if __name__ == "__main__":
	global gpioPins
	
	# pin mux mode bits
	rxEnable = 1 << 5
	rxDisable = 0 << 5

	pullEnable = 0 << 3
	pullDisable = 1 << 3

	pullUp = 1 << 4
	pullDown = 0 << 4

	### All of the different states to support
	# note, first of each list will be default (rxDisable_pullNone with the below)!

	rxEnableValues = [	# in the format (name, value applied to mask)
		("rxDisable", rxDisable),		# disable
		("rxEnable", rxEnable),		# enable
	]

	pullValues = [
		("pullNone", pullDisable ),	# disable
		("pullUp", pullEnable | pullUp ),		# up and enable
		("pullDown", pullEnable | pullDown),		# down and enable
	]

	combinations = getCombinations([rxEnableValues, pullValues])	# gets all the combinations of the state values

	print "State name, mux mode value:"
	states = []
	for combo in combinations:
		names, values = zip(*combo)
		stateName = "_".join(names) 
		muxMode = reduce(operator.or_, values, 0)	# or all of the values together
		states.append(stateName, muxMode)
		print "  %s:" % stateName, hex(muxMode)

	filenames = generateDTSFiles(gpioPins, states)
	generateCompileScript(filenames)
	generateInstallScript(filenames)