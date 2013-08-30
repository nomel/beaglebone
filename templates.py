def populate(template, values):
	# template is a string containing tags. the tags get replaced with the entries from the values dictionary.
	# example:
	#   > template = "hello there <<your name>>!"
	#   > values = {"your name": "bukaroo banzai"}
	#   > populateTemplate( template, values)
	#   "hello there bukaroo banzai!"
	result = template["text"]
	name = "None"
	try:
		for name in template["parameters"]:
			result = result.replace("<<%s>>" % name, str(values[name]))
	except KeyError:
		print "Template value dictionary is missing the entry:", name
	return result

### dts file template
dtsContents = {
	"parameters": ("part number", "header names", "hardware names", "fragments"),
	"text": """/*
* Easy gpio mux control of <<header names>> (<<hardware names>>)
*/
/dts-v1/;
/plugin/;

/ {
	compatible = "ti,beaglebone", "ti,beaglebone-black";

	/* identification */
	part-number = "<<part number>>";
	/* version = "00A0"; */

	/* state the resources this cape uses */
	exclusive-use =
		/* the pin header uses */
		<<header names>>,

		/* the hardware IP uses */
		<<hardware names>>;
	
	<<fragments>>
};
"""
}

### fragment template
fragment = {
	"parameters": ("index", "header name", "clean header name", "state name", "gpio offset", "mux mode"),
	"text": """
	/* <<state name>> state */
	fragment@<<index>> {
		target = <&am33xx_pinmux>;
		__overlay__ {
			gpio_<<clean header name>>_<<state name>>: pinmux_gpio_<<header name>>_<<state name>> {
				pinctrl-single,pins = <
					<<gpio offset>>	<<mux mode>>
				>;
			};
		};
	};
"""
}

### pinctrlTemplate template
pinctrl = {
	"parameters": ("index", "clean header name", "state name"),
	"text": """pinctrl-<<index>> = <&gpio_<<clean header name>>_<<state name>>>;"""
}

pinmuxHelper = {
	"parameters": ("index", "header name", "state names list", "pinctrl list"),
	"text": """
	fragment@<<index>> {
		target = <&ocp>;
		__overlay__ {

			gpio_<<header name>>_helper {
				compatible = "bone-pinmux-helper";
				status = "okay";
				pinctrl-names = <<state names list>>;
				<<pinctrl list>>
			};
		};
	};
"""
}