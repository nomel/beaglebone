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
	( "P8.3", "gpio1_6", 0x018, 6, 7 ),
	( "P8.4", "gpio1_7", 0x01C, 7, 8 ),
	( "P8.5", "gpio1_2", 0x008, 2, 9 ),
	( "P8.6", "gpio1_3", 0x00C, 3, 10 ),
	( "P8.7", "gpio2_2", 0x090, 36, 11 ),
	( "P8.8", "gpio2_3", 0x094, 37, 12 ),
	( "P8.9", "gpio2_5", 0x09C, 39, 13 ),
	( "P8.10", "gpio2_4", 0x098, 38, 14 ),
	( "P8.11", "gpio1_13", 0x034, 13, 15 ),
	( "P8.12", "gpio1_12", 0x030, 12, 16 ),
	( "P8.13", "gpio0_23", 0x024, 9, 17 ),
	( "P8.14", "gpio0_26", 0x028, 10, 18 ),
	( "P8.15", "gpio1_15", 0x03C, 15, 19 ),
	( "P8.16", "gpio1_14", 0x038, 14, 20 ),
	( "P8.17", "gpio0_27", 0x02C, 11, 21 ),
	( "P8.18", "gpio2_1", 0x08C, 35, 22 ),
	( "P8.19", "gpio0_22", 0x020, 8, 23 ),
	( "P8.20", "gpio1_31", 0x084, 33, 24 ),
	( "P8.21", "gpio1_30", 0x080, 32, 25 ),
	( "P8.22", "gpio1_5", 0x014, 5, 26 ),
	( "P8.23", "gpio1_4", 0x010, 4, 27 ),
	( "P8.24", "gpio1_1", 0x004, 1, 28 ),
	( "P8.25", "gpio1_0", 0x000, 0, 29 ),
	( "P8.26", "gpio1_29", 0x07C, 31, 30 ),
	( "P8.27", "gpio2_22", 0x0E0, 56, 31 ),
	( "P8.28", "gpio2_24", 0x0E8, 58, 32 ),
	( "P8.29", "gpio2_23", 0x0E4, 57, 33 ),
	( "P8.30", "gpio2_25", 0x0EC, 59, 34 ),
	( "P8.31", "gpio0_10", 0x0D8, 54, 35 ),
	( "P8.32", "gpio0_11", 0x0DC, 55, 36 ),
	( "P8.33", "gpio0_9", 0x0D4, 53, 37 ),
	( "P8.34", "gpio2_17", 0x0CC, 51, 38 ),
	( "P8.35", "gpio0_8", 0x0D0, 52, 39 ),
	( "P8.36", "gpio2_16", 0x0C8, 50, 40 ),
	( "P8.37", "gpio2_14", 0x0C0, 48, 41 ),
	( "P8.38", "gpio2_15", 0x0C4, 49, 42 ),
	( "P8.39", "gpio2_12", 0x0B8, 46, 43 ),
	( "P8.40", "gpio2_13", 0x0BC, 47, 44 ),
	( "P8.41", "gpio2_10", 0x0B0, 44, 45 ),
	( "P8.42", "gpio2_11", 0x0B4, 45, 46 ),
	( "P8.43", "gpio2_8", 0x0A8, 42, 47 ),
	( "P8.44", "gpio2_9", 0x0AC, 43, 48 ),
	( "P8.45", "gpio2_6", 0x0A0, 40, 49 ),
	( "P8.46", "gpio2_7", 0x0A4, 41, 50 ),
	( "P9.11", "gpio0_30", 0x070, 28, 51 ),
	( "P9.12", "gpio1_28", 0x078, 30, 52 ),
	( "P9.13", "gpio0_31", 0x074, 29, 53 ),
	( "P9.15", "gpio1_16", 0x040, 16, 54 ),
	( "P9.17", "gpio0_4", 0x15C, 87, 55 ),
	( "P9.18", "gpio0_5", 0x158, 86, 56 ),
	( "P9.19", "gpio0_13", 0x17C, 95, 57 ),
	( "P9.20", "gpio0_12", 0x178, 94, 58 ),
	( "P9.21", "gpio0_3", 0x154, 85, 59 ),
	( "P9.22", "gpio0_2", 0x150, 84, 60 ),
	( "P9.23", "gpio1_17", 0x044, 17, 61 ),
	( "P9.24", "gpio0_15", 0x184, 97, 62 ),
	( "P9.25", "gpio3_21", 0x1AC, 107, 63 ),
	( "P9.26", "gpio0_14", 0x180, 96, 64 ),
	( "P9.27", "gpio3_29", 0x1A4, 105, 65 ),
	( "P9.28", "gpio3_17", 0x19C, 103, 66 ),
	( "P9.29", "gpio3_15", 0x194, 101, 67 ),
	( "P9.30", "gpio3_16", 0x198, 102, 68 ),
	( "P9.31", "gpio3_14", 0x190, 100, 69 ),
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
		states.append((stateName, muxMode))
		print "  %s:" % stateName, hex(muxMode)

	filenames = generateDTSFiles(gpioPins, states)
	generateCompileScript(filenames)
	generateInstallScript(filenames)
