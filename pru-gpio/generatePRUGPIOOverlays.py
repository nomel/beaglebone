# Generates device tree overlays for runtime config of every gpio pin.
# 	creates dts files, compile script, and install script
#
# Usage:
#   python generateGPIOOverlays.py	# generates the dts files in the dts directory.
#	cd generated
#   sh compile.sh
#   sh install.sh
# 
# Set P8.30 to pru gpio 11, output:
#	echo prugpio-P8.29 > /sys/devices/bone_capemgr.*/slots
#	echo output > /sys/devices/ocp*/prugpio-P8.29_*/state

import itertools
import operator 
import templates

pru1Pins = [
    #PRU1
    # format is ( header name, offset, (hard ip name for input, hard ip name for output), (mux for input, mux for output))
    ( "P8.20", 0x084, ("pr1_pru1_pru_r31_13", "pr1_pru1_pru_r30_13"), (6, 5)), 
    ( "P8.21", 0x080, ("pr1_pru1_pru_r31_12", "pr1_pru1_pru_r30_12"), (6, 5)), 
    ( "P8.27", 0x0E0, ("pr1_pru1_pru_r31_8", "pr1_pru1_pru_r30_8"), (6, 5)), 
    ( "P8.28", 0x0E8, ("pr1_pru1_pru_r31_10", "pr1_pru1_pru_r30_10"), (6, 5)), 
    ( "P8.29", 0x0E4, ("pr1_pru1_pru_r31_9", "pr1_pru1_pru_r30_9"), (6, 5)), 
    ( "P8.30", 0x0EC, ("pr1_pru1_pru_r31_11", "pr1_pru1_pru_r30_11"), (6, 5)), 
    ( "P8.39", 0x0B8, ("pr1_pru1_pru_r31_6", "pr1_pru1_pru_r30_6"), (6, 5)), 
    ( "P8.40", 0x0BC, ("pr1_pru1_pru_r31_7", "pr1_pru1_pru_r30_7"), (6, 5)), 
    ( "P8.41", 0x0B0, ("pr1_pru1_pru_r31_4", "pr1_pru1_pru_r30_4"), (6, 5)), 
    ( "P8.42", 0x0B4, ("pr1_pru1_pru_r31_5", "pr1_pru1_pru_r30_5"), (6, 5)), 
    ( "P8.43", 0x0A8, ("pr1_pru1_pru_r31_2", "pr1_pru1_pru_r30_2"), (6, 5)), 
    ( "P8.44", 0x0AC, ("pr1_pru1_pru_r31_3", "pr1_pru1_pru_r30_3"), (6, 5)), 
    ( "P8.45", 0x0A0, ("pr1_pru1_pru_r31_0", "pr1_pru1_pru_r30_0"), (6, 5)), 
    ( "P8.46", 0x0A4, ("pr1_pru1_pru_r31_1", "pr1_pru1_pru_r30_1"), (6, 5)), 
    
    ( "P9.26", 0x180, ("pr1_pru1_pru_r31_16", None), (6, None)),    
]

def getPruGpio(hardwareName):
    # hardware name will look like: pr1_pru1_pru_r31_1
    # the index is the last bit there
    pieces = hardwareName.split("_")
    return pieces[4]

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
                    # reset all the lower counters
                    count[:stateIndex] = stateLengths[:stateIndex]
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
        ( "P8.20", 0x084, ("pr1_pru1_pru_r31_13", "pr1_pru1_pru_r30_13"), (6, 5)), 
        headerName, offset, (inputHardwareName, outputHardwareName), (inputMuxMode, outputMuxMode) = pin

        partNumber = "prugpio-%s" % (headerName)
        version = "00A0"
        filename = "%s-%s" % (partNumber, version)
        
        hardwareName = []
        if inputHardwareName:
            hardwareName += ['"%s"' % inputHardwareName]
        if outputHardwareName:
            hardwareName += ['"%s"' % outputHardwareName]
        
        # template values related to this pin
        values = {
            "header name": headerName,
            "clean header name": headerName.replace(".","_"),
            "version": version,
            "part number": partNumber,
            "header names": '"%s"' % headerName,       	# put quotes around it
            "hardware names": ", ".join(hardwareName),
            "gpio index": getPruGpio(inputHardwareName),
            "type": "prugpio",
        }
        
        fragmentList = []								# list of all the processed fragment templates
        pinctrlList = []								# list of all the processed pinctrl templates
        
        ## fill out all of the fragment and pinctrl templates
        stateNames = []
        index = 0
        for stateName, stateMuxBits, isInput in states:
            if isInput:
                directionMux = inputMuxMode
            else:
                directionMux = outputMuxMode
            if directionMux is None:
                continue
            stateNames.append('"%s"' % stateName)
            # template values related to this state
            stateValues = {
                "index": index,
                "state name": stateName,
                "offset and mux list": "%s %s" % (hex(offset), hex(directionMux | stateMuxBits ))
            }
            values.update(stateValues)
            
            # make the fragment and pinctrl entry for these state values
            fragmentList.append(templates.populate(templates.fragment, values))		
            pinctrlList.append(templates.populate(templates.pinctrl, values))
            
            index += 1
        
        # last fragment entry for pinmux helper
        helperValues =	{
            "index": index,
            "state names list": ", ".join(stateNames),
            "pinctrl list": "\n\t\t\t\t".join(pinctrlList),
        }
        values.update(helperValues)
        fragmentList.append(templates.populate(templates.pinmuxHelper, values))

        index += 1

        # fragment to enable pruss stuffs
        statusValues = {
            "index": index,
            "status": "okay",
        }
        values.update(statusValues)
        fragmentList.append(templates.populate(templates.prussHelper, values))
        
        ## dts template
        dtsValues = {
            "fragments": "".join(fragmentList)
        }
        values.update(dtsValues)
        dtsFileContents = templates.populate(templates.dtsContents, values)
        
        ## write the dts file for this pin!
        print "Writing", filename
        f = open("%s.dts" % filename, "wb")
        try:
            f.write(dtsFileContents)
        finally:
            f.close()
            
        dtsFilenames.append(filename)
        
    return dtsFilenames

def generateCompileScript(dtsFilenames):
    print "Generating compile script."
    f = open("compile.sh", "wb")
    try:
        f.write("echo Compiling dts files...\n")
        command = "echo %s.dts -\> %s.dtbo\ndtc -O dtb -o %s.dtbo -b 0 -@ -I dts %s.dts\n"
        for filename in dtsFilenames:
            f.write(command % (filename, filename, filename, filename))
        f.write("echo Done.")
    finally:
        f.close()
    print "Done."	
    
def generateInstallScript(dtsFilenames):
    print "Generating install script."
    f = open("install.sh", "wb")
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

    # since the pru pins are unidirectional and there's no way to read the physical pin state like with gpio, no need for this
    # rxEnableValues = [
        # # in the format (name, value applied to mask)
        # ("rxDisable", rxDisable),
        # ("rxEnable", rxEnable),
    # ]

    directionModeValues = [
        ("input", 0),
        ("output", 0),
    ]
    
    pullValues = [
        ("pullNone", pullDisable ),
        ("pullUp", pullEnable | pullUp ),
        ("pullDown", pullEnable | pullDown),
    ]
    
    # all the combinations of the state values
    combinations = getCombinations([directionModeValues, pullValues])

    print "State name, mux mode value:"
    states = []
    for combo in combinations:
        names, values = zip(*combo)
        
        muxMode = reduce(operator.or_, values, 0)	# or all of the values together
        stateName = "_".join(names)                
        # if it's input, enable the receiver
        isInput = "input" in names
        if isInput:
            muxMode |= rxEnable
        else:
            # for output, only include options without pull resistors.
            if "pullNone" not in names:
                continue
            stateName = "output"    # don't need a pull resistor since it doesn't make sense for pru output.
            muxMode |= rxDisable
        states.append((stateName, muxMode, isInput))
        print "  %s:" % stateName, hex(muxMode)

    filenames = generateDTSFiles(pru1Pins, states)
    generateCompileScript(filenames)
    generateInstallScript(filenames)
