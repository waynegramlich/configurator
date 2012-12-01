#!/usr/bin/python

## @package data_structures
#
# Configurator data structures.
#
# The data structures are basically one-to-one with corresponding
# XML file data structures.
#
# Due to the nature of Python, the code generation code currently
# hangs off individual the individual class objects.

import os
import sys
import re
import xml.etree.ElementTree as ET

## @class Node
#
# Base class for tree displayable objects.
#
# The *Node* class is a common base class used for sub-classes that
# need to be displayable in the GUI as a part of a tree widget.

class Node:

    ## @brief *Node* Constructor
    # @param self       *Node* object being initialized.
    # @param class_name *str* The textual name of the sub-class.
    # @param text	*str* Text to show on tree widget
    # @param icon_name  *str* Name of the icon to show next to object (or None).
    # @param sub_nodes  *list* The list of sub-class object under this *Node*.
    # @param style      *Style* object used for formatting.
    #
    # This method initializes *Node* with the *class_name* (e.g.
    # "Module_Use", "Selection", etc.), the icon name from the
    # Icons directory, *sub_nodes* which is a list of *Node*
    # object that constitute the children of *self*, and *style*
    # which is a *Style* object that specifies the format of
    # generated code.

    def __init__(self, class_name, text, icon_name, sub_nodes, style):

	# Check argument types:
	assert isinstance(class_name, str)
	assert isinstance(text, str)
	assert icon_name == None or isinstance(icon_name, str)
	assert sub_nodes == None or isinstance(sub_nodes, list)
	assert isinstance(style, Style)
	if sub_nodes != None:
	    for sub_node in sub_nodes:
		assert isinstance(sub_node, Node)

	# Load up *self*:
	self.class_name = class_name
	self.icon_name = icon_name
	self.text = text
	self.style = style
	self.sub_nodes = sub_nodes

    ## @brief Recursively find parent of *self* starting from *root_node*.
    #  @param self *Node* object to find parent of.
    #  @param root_node *Node* object to start search from
    #  @result The parent *Node* object (or *None* if not found.)
    #
    # Since the *Node* class does not maintain parent back pointers,
    # finding a parent object actually requires a recursive search
    # from the top most root *Node*.

    def parent_index_find(self, root_node):

	# Check argument types:
	assert isinstance(root_node, Node)
	
	result_node = None
	result_index = -1
	sub_nodes = root_node.sub_nodes
	if sub_nodes != None:
	    for index in range(len(sub_nodes)):
		sub_node = sub_nodes[index]
		# We are done if *sub_node* matches:
		if sub_node == self:
                    result_node = root_node
		    result_index = index

		# We are done if one nodes under *sub_node* matches:
		sub_node, sub_index = self.parent_index_find(sub_node)
		if sub_node != None:
		    result_node = sub_node
		    result_index = sub_index
	result_name = "<none>"
	if result_node != None:
	    result_name = result_node.name

	#print "parent_index_find({0}, {1})=>{2}, {3}". \
	#  format(self.name, root_node.name, result_name, result_index)

	return result_node, result_index

    ## @brief Method print *self* indented by *indent*.
    #  @param self *Node* object to write out.
    #  @param indent *int* that specifies how much to indent by.
    #
    # This provides a quick and dirty interface for debugging.

    def show(self, indent):

	# Check argument types:
	assert isinstance(indent, int)

	print "{0}{1}:{2}".format("  " * indent, self.class_name, self.name)
	sub_nodes = self.sub_nodes
	if sub_nodes != None:
	    for sub_node in sub_nodes:
		sub_node.show(indent + 1)

    ## @brief Append *sub_node* to the children sub nodes of *self*.
    #  @param self *Node* to whose children to append to
    #  @param sub_node *Node* to append children sub nodes
    #
    # This method will append *sub_node* to the end of the list of children
    # sub nodes of *self*.

    def sub_node_append(self, sub_node):

	# Check argument types:
	assert isinstance(sub_node, Node)

	sub_nodes = self.sub_nodes
	if sub_nodes == None:
	    sub_nodes = []
	    self.sub_nodes = sub_nodes
	sub_nodes.append(sub_node)

    ## @brief Method writes *self* to *out_stream* indented by *indent*.
    #  @param self *Node* object to write out.
    #  @param indent *int* that specifies how much to indent by.
    #  @param out_stream *file* that specifies an output stream to write to.
    #
    # This method will write *self* in XML format to *out_stream* indented by
    # *indent*.  This method should be overridden to provide the correct
    # tags and attributes .

    def xml_write(self, indent, out_stream):

	# Check argument types:
	assert isinstance(indent, int)
	assert isinstance(out_stream, file)

	print self
	assert False, "No write method for {0} Node". format(str(type(self)))

## @class Classification
#
# One Classification path for module
#
# A module can be shown in the "Selections" window in multiple locations.
# Each location is defined by a *Classification*.  A *Classification*
# corresponds to the <Classification ... /> tag in module XML file.
# The attributes of the <Classification ... /> tag are *Level1*,
# *Level2*, etc.  The *Level1* attribute is typically one of "Buses",
# "Categories", or "Vendors".  Each level subsequent level nests one
# level deeper in the nesting tree.

class Classification():

    ## @brief *Classification* constructor
    #  @param self *Classification* object to initialize
    #  @param classification_element *Element* tree element to read from
    #  @param style *Style* object to control generated code formatting.
    #
    # This method will extract the classification information from
    # the XML *classification_element* and store the result into *self*.

    def __init__(self, classification_element, style):

	# Check argument types:
	assert isinstance(classification_element, ET.Element)
	assert classification_element.tag == "Classification"
	assert isinstance(style, Style)

	# Get the attributes
	attributes = classification_element.attrib

	# Iterate through each of the 10 possible level attributes
	# and append the values to *levels*:
	levels = []
	for index in range(1, 10):
	    level_name = "Level{0}".format(index)
	    if level_name in attributes:
		# Found one, append it to *levels*
		levels.append(attributes[level_name])
	    else:
		# No more Level attributes, we are done:
		break
	    
	# Stash the values away in to *self*:
	self.levels = levels
	self.style = style

## @class Description
#
# A Description of module function or register
#
# Each module has a textual description in its defining XML file.
# This class captures the descriptive text.  This corresponds to:
#
#        <Description>
#          Text that describes function or register goes here.
#        </Description>
#
# in the XML file.

class Description:

    ## @brief *Description* Constructor
    #  @param description_element *Element* that contains the Description XML
    #  @param style *Style* object that specifies how to format generate code.
    #
    # Initialize a *Description* object using *description_element*
    # for the XML information and *style* for the formatting style.

    def __init__(self, description_element, style):

	# Check argument types:
	assert isinstance(description_element, ET.Element)
	assert description_element.tag == "Description", \
	  "Need <Description> tag"
	assert isinstance(style, Style)

	# Load up *self*:
	self.style = style
	self.text = description_element.text

    ## @brief Return the *Description* object from *parent_element*
    #  @param parent_element *Element* parent containing XML description
    #  @param style *Style* object that specifies how to format generate code.
    #  @result *Description* extracted from *parent_element*
    #
    # This static method is responsible for ensuring that there is one
    # and only one <Description ...> tag underneight *parent_element*.
    # The resulting *Description* is returned.

    @staticmethod
    def extract(parent_element, style):

	# Extract all *descriptions* from *parent_element*:
	descriptions = []
	for description_element in parent_element.findall("Description"):
	    descriptions.append(Description(description_element, style))

	# Make sure there is exacty one *description*:
	if len(descriptions) == 1:
	    # We have exactly one; return it:
	    description = descriptions[0]
	else:
	    # We either have none, or more than one, generate error message:
	    description = None
	    print "{0}:<{1} Name='{2}'...> has {3} <Description> tags". \
	      format(XML.line_number(parent_element), parent_element.tag,
		parent_element.attrib["Name"], len(descriptions))

	return description

## @class Function
#
# One Function of a module
#
# A module can have one or more functions that can be invoked via
# a remote procedure call.  A function has zero, one, or more parameters
# and zero, one, or more results.  This shows up in the XML files as:
#
#        <Function Name="..." Number="..." Brief="...">
#          <Description>
#            *Description goes here*
#          </Description>
#          <Parameter Name="..." Type="..." Brief="..." />
#          ...
#          <Result Name="..." Type="..." Brief="..." />
#          ...
#        </Function>

class Function(Node):

    ## @brief Function constructor
    #  @param self *Function* object to initialize
    #  @param function_element *Element* containing XML to extract from
    #  @param style *Style* object that specifies how to format generate code.
    #
    # This method extacts information about a remote procedure call
    # function from *function_element* and stuffs it into *self*.

    def __init__(self, function_element, style):

	# Check argument type:
	assert isinstance(function_element, ET.Element)
	assert isinstance(style, Style)
	assert function_element.tag == "Function"

	# Extract the <Function ...> attributes:
	attributes = function_element.attrib
	name = attributes["Name"]
	brief = attributes["Brief"]
	number = int(attributes["Number"])

	# We need to have *style* loaded into *self* for *format*() to work.
	self.name = name
	self.style = style

	# Build a signature for the function:
	signature = "{0:r}(".format(self)

	# Iterate over all the parameters:
	prefix = ""
	parameters = []
	for parameter_element in function_element.findall("Parameter"):
	    parameter = Parameter(parameter_element, style)
	    parameters.append(parameter)
	    signature += prefix + parameter.name
	    prefix = ", "
	signature += ")"

	# Iteratate over all the results:
	prefix = " => "
	results = []
	for result_element in function_element.findall("Result"):
	    result = Result(result_element, style)
	    results.append(result)
	    signature += prefix + result.name

	# Load up the rest of *self*:
	self.brief = brief
	self.description = Description.extract(function_element, style)
	self.number = number
	self.parameters = parameters
	self.results = results

	# Initalize the parent *Node* base class.
	Node.__init__(self, "Function", signature, None, None, style)

    ## @brief Format *self* using *fmt* string.
    #  @param self *Function* to use for formatting.
    #  @param fmt *str* that specifies the format to use
    #  @result *str* Formatted string is returned
    #
    # Format *self* using *fmt* to control formatting and return the
    # formatted string.  The allowed formatting strings are:
    #
    #   * 'r' returns just the routine name in the appropriate style
    #   * 'S' returns C/C++ output signature.
    #   * 'Sxxx' returns the C/C++ output signature with 'xxx' spliced
    #     in before the routine name.  This is used to splice a class
    #     name in front of the routine name.  For example, 'SClass_Name::'
    #     will return "Class_name::{routine_name}(...)".
    #   * 's' returns a simplified signature that has just the a
    #     routine name, parameter name and result names in the form
    #     "routine_name(parameter_names, ...) => result_names, ...

    def __format__(self, fmt):

	# Check argument types:
	assert isinstance(fmt, str)

	# Dispatch on *fmt*:
	style = self.style
	if fmt == "":
            # Error:
	    result = "@Function@"
	elif fmt == 'r':
            # Routine name:
	    result = style.routine_name(self.name)
	elif fmt[0] == 'S':
	    # Signature:
	    lexemes = []

	    # Figure out the return type:
	    results = self.results
	    results_length = len(results)
	    return_type = "void"
	    if results_length != 0:
		return_type = results[0].type

	    # Generate return type
	    lexemes.append("{0} {1}{2:r}(".format(return_type, fmt[1:], self))

	    # Output the parameters:
	    prefix = ""
	    for parameter in self.parameters:
		lexemes.append("{0}{1:c}".format(prefix, parameter))
	        prefix = ", "

	    # If there are more than 1 return result, add them to the
	    # parameter list as well:
	    if results_length >= 2:
		for index in range(1, results_length):
		    result = results[index]
		    lexemes.append("{0}{1:t} *{1:n}".format(prefix, result))
		    prefix = ", "

            # Wrap up:
	    lexemes.append(")");
	    result = "".join(lexemes)
	elif fmt[0] == 's':
	    # Start with the routine name:
	    result = "{0:r}(".format(self)

	    # Append the parameters:
	    prefix = ""
	    for parameter in self.parameters:
		result += "{0}{1:n}".format(prefix, parameter)
	        prefix = ", "
	    result += ")"

	    # Append the return results:
            results = self.results
            prefix = " => "
            for result_node in self.results:
		result += "{0}{1:n}".format(prefix, result_node)
		prefix = ", "
	else:
	    # Error:
	    result = "@Function:{0}@".format(fmt)
	return result

    ## @brief Write the C++ method declaration for *self* to *out_stream*.
    #  @param self *Function* object to use for information
    #  @param module *Module* (Currently unused)
    #  @param out_stream *file* output stream to output to
    #
    # This routine will output a chunk of C++ code to *out_stream*
    # that corresponds to method declaration in C++ class definition:
    # The code looks roughly as follows:
    #
    #        // BRIEF
    #        RT1 FUNCTION(PT1 PN1,...,PTn PNn,RT2 RN2,...,RTn RNn);
    #
    # where
    #
    #  * FUNCTION is the function name
    #  * BRIEF is the 1 line comment brief
    #  * PNi is the i'th Parameter Name
    #  * PTi is the i'th Parameter Type
    #  * RNi is the i'th Result Name
    #  * RTi is the i'th Result Type

    def cpp_header_write(self, module, out_stream):

	# Check argument types:
	assert isinstance(module, Module)
	assert isinstance(out_stream, file)

	# Output: "// BRIEF"
	style = self.style
	out_stream.write("{0:i}// {1}\n".format(style, self.brief))

	# Output: "RT1 FUNCTION(PT1 PN1,...,PTn PNn,RT2 RN2,...,RTn RNn);"
	out_stream.write("{0:i}{1:S};\n\n".format(style, self))

    ## @brief Write local C++ RPC code for *self* to *out_stream*.
    #  @param self *Function* to use for parameters and return results
    #  @param module *Module* to use for module name and the like.
    #  @param out_stream *file* to write everything out to.
    #
    # This method will output the local remote procedure call C++ code
    # for *function out to *out_stream*.  The code looks basically
    # like this:
    #
    #        // FUNCTION: BRIEF
    #        RT1 MODULE::FUNCTION(PT1 PN1,...,PTn PNn, RT2 *RN2,...,RTn *RNn) {
    #          RT1 RN1;
    #          ...
    #          RTn RNn;
    #          //////// Edit begins here: {FUNCTION_NAME}
    #          //////// Edit ends here: {FUNCTION_NAME}
    #          return RN1;
    #        }
    #
    # where
    #
    #  * FUNCTION is the function name
    #  * BRIEF is the 1 line comment brief
    #  * MODULE is the module name
    #  * PNi is the i'th Parameter Name
    #  * PTi is the i'th Parameter Type
    #  * RNi is the i'th Result Name
    #  * RTi is the i'th Result Type

    def cpp_local_source_write(self, module, out_stream):

	# Check argument types:
	assert isinstance(module, Module)
	assert isinstance(out_stream, file)

	# Grab some values from *self*:
	style = self.style
	name = self.name
	results = self.results
	results_length = len(results)

	# Output "// FUNCTION: BRIEF"
	out_stream.write("// {0:r}: {1}\n".format(self, self.brief))

 	# Output:
	#   "RT1 MODULE::FUNC(PT1 PN1,...,PTn PNn, RT2 *RN2,...,RTn *RNn) {"

	# Compute the signature with {class_name}:: prepended to function name:
	module_type_name = "{0:t}".format(module)
	format_string = "{0:S" + module_type_name + "::}{1:b}"
	#print "format_string='{0}'".format(format_string)
	out_stream.write(format_string.format(self, style))

	# Output variables for all the results:
	for result in results:
	    # Output: "RTi RNi;"
            out_stream.write("{0:i}{1:t} {1:n};\n".format(style, result))

	# Output the code fence::
        #	//////// Edit begins here: {FUNCTION_NAME}
        #	//////// Edit ends here: {FUNCTION_NAME}
	module.fence_write("{0:r}".format(self).upper(), out_stream)

	# Output: "return RN1;":
	if results_length != 0:
	    out_stream.write("{0:i}return {1};\n". \
	      format(style, self.results[0].name))

	# Output: "}":
	out_stream.write("{0:e}\n".format(style))

    ## @brief Write C++ code for RPC request handing for *self* to *out_stream*
    #  @param self *Function* to process
    #  @param offset *int* offset to use for function
    #  @param module_name *str* Module name to use
    #  @param out_stream *file* to write output to
    #
    # This method will output *self* to *out_stream* as a **case** clause
    # as part of a **switch** statement.  The basic format of the code
    # that is generated looks as follows:
    #
    #        case NUMBER: {
    #          // FUNCTION_NAME: BRIEF
    #          PN1 = maker_bus->PT1_get();
    #          ...
    #          PNn = maker_bus->PTn_get();
    #          RT1 RN1;
    #          ...
    #          RTn RNn;
    #          if (execute_mode) {
    #            RN1 = FUNCTION_NAME(PN1,...PNn,&RN2,...,&RNn);
    #            maker_bus->RT2_put(RN2);
    #            ...
    #            maker_bus->RTn_put(RNn);
    #            break;
    #          }
    #        }
    #
    # where
    #
    #  * NUMBER is the RPC number
    #  * FUNCTION_NAME is the function name
    #  * BRIEF is the 1 line comment brief
    #  * PNi is the i'th Parameter Name
    #  * PTi is the i'th Parameter Type
    #  * RNi is the i'th Result Name
    #  * RTi is the i'th Result Type

    def ino_slave_write(self, offset, variable_name, out_stream):

	# Check argument types:
	assert isinstance(offset, int)
	assert isinstance(variable_name, str)
	assert isinstance(out_stream, file)

	# Grab some values out of *self*:
	brief = self.brief
	name = self.name
	number = self.number
	parameters = self.parameters
	results = self.results
	results_length = len(results)
	style = self.style

	# Output: "case NUMBER: {"
	out_stream.write("{0:i}case {1}:{0:b}".format(style, offset + number))

	# Output: "// FUNCTION_NAME: BRIEF"
	out_stream.write("{0:i}// {1:r}: {2}\n".format(style, self, brief))

	# Fetch the each *parameter* value and stuff into a local variable:
	for parameter in parameters:
            # Output "PNi = maker_bus->PTi_get();"
	    parameter_type = parameter.type
            out_stream.write("{0:i}{1:c} = maker_bus->{2}_get();\n". \
	      format(style, parameter, parameter_type.lower()))
	    
	# Define the variables needed for return values:
	for result in results:
	    # Output: "RT1 RN1;"
            out_stream.write("{0:i}{1:c};\n".format(style, result))

	# Output: "if (execute_mode) {"
	out_stream.write("{0:i}if (execute_mode){0:b}".format(style))

	# Output: "RN1 = " (if needed):
	out_stream.write("{0:i}".format(style))
	if results_length >= 1:
	    out_stream.write("{0:n} = ".format(results[0]))

	# Output: "FUNCTION_NAME(":
	out_stream.write("{0}.{1:r}(".format(variable_name.lower(), self))

	# Output: "PN1,...PNn" (if available):
	prefix = ""
	for parameter in parameters:
            out_stream.write("{0}{1:n}".format(prefix, parameter))
	    prefix = ", "

	# Output: ",&RN2,...,&RNn" (if necessary):
	if results_length > 1:
	    for index in range(1, results_length):
		result = results[index]
		out_stream.write("{0}&{1:n};\n".format(prefix, result))
		prefix = ", "

	# Output: ");" 
	out_stream.write(");\n")

	# Send any results to the send buffer:
	for result in results:
	    # Output: "maker_bus->RTi_put(RNi);"
            out_stream.write("{0:i}maker_bus->{1}_put({2:n});\n". \
	      format(style, result.type.lower(), result))

	# Output: "}"
	out_stream.write("{0:e}".format(style))

	# Output: "break;"
	out_stream.write("{0:i}break;\n".format(style))

	# Output: "}"
	out_stream.write("{0:e}".format(style))

    ## @brief Write remote side RPC code for *self* to *out_stream*.
    #  @param self *Function* to output RPC code for
    #  @param module *Module* to use for module name
    #  @param out_stream *file* to output code to
    #
    # The routine will look something like:
    #
    #	// NAME: BRIEF
    #	RT1 MODULE::FUNCTION(PT1 PN1,...,PTn PNn,RT2 *RN2,...,RTn *RNn) {
    #	    Maker_Bus_Module::command_begin(NUMBER);
    #	    Maker_Bus_Module::PT1_put(P1);
    #	    ...
    #	    Maker_Bus_Module::PTn_put(Pn);
    #	    RT1 R1 = Maker_Bus_Module::RT1_get();
    #	    *RN2 = Maker_Bus_Module::RT2_get();
    #	    ...
    #	    *RNn = Maker_Bus_Module::RTn_get();
    #	    Maker_Bus_Module::command_end();
    #	    return RN1;
    #	}
    #
    # where
    #
    #  * NUMBER is the RPC number
    #  * FUNCTION_NAME is the function name
    #  * BRIEF is the 1 line comment brief
    #  * PNi is the i'th Parameter Name
    #  * PTi is the i'th Parameter Type
    #  * RNi is the i'th Result Name
    #  * RTi is the i'th Result Type

    def cpp_remote_source_write(self, module, out_stream):

	# Check argument types:
	assert isinstance(module, Module)
	assert isinstance(out_stream, file)

	# Grab some values from *self*:
	style = self.style
	name = self.name
	number = self.number
	parameters = self.parameters
	results = self.results
	results_length = len(results)

	# Output: "// NAME: BRIEF"
	out_stream.write("// {0:r}: {1}\n".format(self, self.brief))

	# Output:
        #  "T1 MODULE::FUNCTION(PT1 PN1,...,PTn PNn,RT2 *RN2,...,RTn *RNn) {":
	format_string = "{0:S" + module.name + "::}{1:b}"
	#print "format_string='{0}'".format(format_string)
	out_stream.write(format_string.format(self, style))

	# Output: "Maker_Bus_Module::command_begin(NUMBER);"
	out_stream.write("{0:i}Maker_Bus_Module::command_begin({1});\n". \
	  format(style, number))

	# Output the code to send the parameters over to the module:
	for parameter in parameters:
	    # Output: Maker_Bus_Module::PTi_put(PNi);
	    out_stream.write("{0:i}Maker_Bus_Module::{1}_put({2:n});\n". \
	      format(style, parameter.type.lower(), parameter))

	# Deal with RPC returned results:
	for index in range(results_length):
	    result = results[index]
	    if index == 0:
		# Output: "RT1 RN1 = Maker_Bus_Module::RT1_get();"
		out_stream.write("{0:i}{1} {2} = ". \
		  format(style, result.type, result.name.lower()))
	    else:
	        # Output: "*RNi = Maker_Bus_Module::RTi_get();"
		out_stream.write("{0:i}*{1} = ". \
		  format(style, result.type, result.name.lower()))
            out_stream.write("Maker_Bus_Module::{0}_get();\n". \
	      format(result.type.lower()))

	# Output:  Maker_Bus_Module::command_end();
	out_stream.write("{0:i}Maker_Bus_Module::command_end();\n". \
	  format(style))

	# Output: "return RN1;"
	if results_length != 0:
	    out_stream.write("{0:i}return {1};\n". \
	      format(style, results[0].name.lower()))

	# Output: "}"
	out_stream.write("{0:e}\n".format(style))

    ## @brief Output Python RPC code for *self* to *out_stream*
    #  @param self *Function* to output Python code for
    #  @param out_stream *file* to output Python code to
    #
    # This routine will output remote procedure call code for *self*
    # to *out_stream*.  The code looks as follows:
    #
    #        def FUNCTION(self, PN1, ..., PNn):
    #            # BRIEF
    #            self.request_begin(NUMBER)
    #            self.request_PT1_put(PN1)
    #            ...
    #            self.request_PTn_put(PNn)
    #            self.request_end()
    #            RN1 = self.request_RT1_get()
    #            ...
    #            RNn = self.request_RTn_get()
    #            return RN1, ..., RNn
    #
    # where:
    #
    #  * FUNCTION is the function name
    #  * BRIEF is the 1 line comment brief
    #  * PNi is the i'th Parameter Name
    #  * PTi is the i'th Parameter Type
    #  * RNi is the i'th Result Name
    #  * RTi is the i'th Result Type

    def python_write(self, out_stream):

	# Check argument types:
	assert isinstance(outstream, file)

	# Grab some values from *self*:
	brief = self.brief
	name = self.name
	number = self.number
	parameters = self.parameters
	results = self.results
	style = self.style

	# Output: "def FUNCTION(self, PN1, ..., PNn):":
	out_stream.write("{0:i}def {1:r}(self".format(style, self))
	for parameter in parameters:
	    out_stream.write(", {0:n}".format(parameter))
	out_stream.write("):\n")

	# Indent code body:
	style.indent_adjust(1)

	# Output: "// BRIEF"
	out_stream.write("{0:i}# {1}\n\n".format(style, brief))

	# Output: "self.request_begin(NUMBER)"
	out_stream.write("{0:i}self.request_begin({1})\n". \
	  format(style, number))

	# Send each Parameter:
	for parameter in parameters:
	    # Output: "self.request_PTx_put(PNx)
	    out_stream.write("{0:i}self.request_{1}_put({2:n})\n". \
	      format(style, parameter.type.lower(), parameter))

	# Output: "self.request_end()"
	out_stream.write("{0:i}self.request_end()\n".format(style))

	# Get all return values:
	for result in results:
	    # Output: "RNx = self.request_RTx_get()"
	    out_stream.write("{0:i}{1} = self.response_{2}_get()\n". \
	      format(style, result.name.lower(), result.type.lower()))

	# Output: "return RN1, ..., RNn" (if necessary):
        if len(results) != 0:
	    out_stream.write("{0:i}return ".format(style))
	    prefix = ""
	    for result in results:
		out_stream.write("{0}{1:n}".format(prefix, result))
		prefix = ", "
	    out_stream.write("\n")
	out_stream.write("\n")

	# Restore indentation:
	style.indent_adjust(-1)

## @class Module
#
# One Module device
#
# A *Module* corresponds to an electronic device that can be plugged
# together.  The overall structure of a Module corresponds to an
# <Module ...> tag in an XML file:
#
#        <Module Name="..." Vendor="..." Brief="...">
#          <Overview>
#            Module overview text goes here.
#          </Overview>
#          <Classification /> ...
#          <Register /> ...
#          <Function /> ...
#        </Module>

class Module(Node):

    ## @brief Module constructor
    #  @param self *Module* to initialize
    #  @param module_element *ET.Element* to initialize from
    #  @param path *str* file path to .xml file read in
    #  @param style *Style* object that specifies how to format generate code.
    # 
    # This method will initialize the contents of *self* by read the
    # associated XML infromation from *module_element.

    def __init__(self, module_element, path, style):

	# Check arugment types:
	assert isinstance(module_element, ET.Element) and \
	  module_element.tag == "Module"
	assert isinstance(style, Style)

	# Extract all classifications from <Classification ...> tags:
	classifications = []
	for classification_element in module_element.findall("Classification"):
	    classification = Classification(classification_element, style)
	    classifications.append(classification)

	# Extract all of the registers from <Register ...> tags:
	registers = []
	for register_element in module_element.findall("Register"):
	    registers.append(Register(register_element, style))

	# Extract all of the functions from <Function ...> tags:
	functions = []
	for function_element in module_element.findall("Function"):
	    functions.append(Function(function_element, style))

	# Extract overview form <Overview> tag:
	overview = Overview.extract(module_element, style)

	# Extract required attributes:
	attributes = module_element.attrib
	name = attributes["Name"]
	vendor = attributes["Vendor"]

	# Deal with optional attributes:
	address_re = "^[0-9]+$"
	if "Address_RE" in attributes:
	    address_re = attributes["Address_RE"]
	sub_class = None
	if "Sub_Class" in attributes:
	    sub_class = attributes["Sub_Class"]
	generate = False
	if "Generate" in attributes:
	    generate = attributes["Generate"] != 0

	# Fill in the contents of *self*:
	self.classifications = classifications
	self.address_re = address_re
	self.name = name
	self.fence_begin = "  //////// Edit begins here:"
	self.fence_end = "  //////// Edit ends here:"
	self.functions = functions
	self.generate = generate
	self.registers = registers
	self.fences = {}
	self.overview = overview
	self.path = path
	self.style = style
	self.sub_class = sub_class
	self.vendor = vendor

	# Construct a sorted list of functions and registers:
	functions_and_registers = []
	for function in functions:
	    functions_and_registers.append(function)
	for register in registers:
	    functions_and_registers.append(register)
	functions_and_registers.sort(key=lambda fr: fr.name)
	if len(functions_and_registers) == 0:
	    functions_and_registers = None

	# Initilize the parent *Node* object:
	Node.__init__(self,
	  "Module", name, None, functions_and_registers, style)

    ## @brief Return formatted version of *self* using *fmt* for format control.
    #  @param self *Module* to format
    #  @param fmt A *str* that controls formatting
    #  @result *str* formatted result string
    #
    # This mehod will return a formated version of *self* using *fmt* to
    # control the formatting.  *fmt* must be one of:
    #
    #  * 'n' returns the module name.
    #  * 't' returns the module as a C/C++ type name

    def __format__(self, fmt):

	# Check argument types:
	assert isinstance(fmt, str)

	# Dispatch on *fmt*:
	if fmt == 'n':
	    result = self.name
	elif fmt == 't':
	    result = self.name.replace(" ", "_")
	else:
	    result = "@Module:{0}@".format(fmt)
	return result

    ## @brief Write C++ header file for *self* out to *file_name*.
    #  @param self *Module* to generate C++ for
    #  @param file_name *str* file name to open and write C++ into
    #  @param with_fences *bool* if *True*, causes fences to be written as well
    #
    # This method will write out a C++ header file that contains declarations
    # for all the functions and registers associated with *module*.

    def cpp_header_write(self, file_name, with_fences):

	# Grab some values from *self*:
	style = self.style
	name = self.name

	# Read in any fenced code from {file_name}:
	if with_fences:
	    self.fences_read(file_name)

	# Now write out the new verision of *file_name* with the
	# edits from the previous file retained:
	out_stream = open(file_name, "w")
	
	# Let people know if they should edit this file:
	out_stream.write("// Generated file: ")
	if with_fences:
	    out_stream.write("only edit in designated area!\n\n")
	else:
            out_stream.write("do not edit!\n\n")

	# Output an idempotent header file.  Use base of *file_name*
	# without preceeding directories or following suffix as the
	# #ifdef variable:
	file_base_pattern = re.compile("/(\w+)\.h")
	file_base = file_base_pattern.search(file_name).group(1).upper()
	#print "file_base='{0}'".format(file_base)

	# Write out the two preprocesor lines:
	out_stream.write("#ifndef {0}_H\n".format(file_base))
	out_stream.write("#define {0}_H\n\n".format(file_base))

	# Output the include files:
	#FIXME: This should not be wired in like this!!!
	out_stream.write("#include <MB7.h>\n")
	out_stream.write("\n")

	# Write out a fence:
	if with_fences:
	    self.fence_write("TOP_LEVEL", out_stream)
	    out_stream.write("\n")

	# Start the class declaration:
	out_stream.write("class {0:t} : public Maker_Bus_Module".format(self))
	sub_class = self.sub_class
	if sub_class != None and with_fences:
	    out_stream.write(", public {0} ".format(sub_class))
	out_stream.write("{0:b}".format(style))

	# All the methods are public:
	out_stream.write("{0:i}public:\n".format(style))
	style.indent_adjust(1)

	# Generate the constructor signature for the class:
	out_stream.write("{0:i}// Constructor\n".format(style))
	out_stream.write("{0:i}{1:t}(UByte address);\n\n".format(style, self))

	# Generate method declarations for each *register*:
	for register in self.registers:
	    register.cpp_header_write(self, out_stream)

	# Generate method declarations for each *function*:
	for function in self.functions:
	    function.cpp_header_write(self, out_stream)

	# Write out the *retained_lines* surrounded by a "fence":
	if with_fences:
	    self.fence_write("PRIVATE", out_stream)

	# Close out the class declaration:
	style.indent_adjust(-1)
	out_stream.write("{0:E}\n".format(style))

	# Close off idempotent #ifdef:
	out_stream.write("#endif // {0}_H\n".format(file_base))

	# All done:
	out_stream.close()

    ## @brief Write a local C++ header file for *self* to *file_name*
    #  @param self *Module* to write C++ header for
    #  @param file_name *str* file name to open and write C++ into
    #
    # This method will write a local C++ header file for *self* into the
    # file name *file_name*.  If *file_name* does  not exist, it will be
    # created.  If *file_name* does exist, it is replaced such that all
    # the code in the fenced off area inside the source code is retained.

    def cpp_local_header_write(self, file_name):
	assert isinstance(file_name, str)
	self.cpp_header_write(file_name, True)


    ## @brief Write local C++ code for *self* into *file_name*
    #  @param self *Module* to geneate C++ code for
    #  @param file_name *file_name* file name to open and pour C++ code into
    #
    # This method will write out local C++ code for *self* into *file_name*.
    # This basically consists of of some include files, a class constructor
    # for *self*, and each of the register and function methods.

    def cpp_local_source_write(self, file_name):

	# Check argument types:
	assert isinstance(file_name, str)

	# Grab some values from *self*:
	style = self.style
	name = self.name

	# Read in the fenced code from *file_name*:
	self.fences_read(file_name)

	# Now write out the new verision of *file_name* with the
	# edits from the previous file retained:
	out_stream = open(file_name, "w")

	# Output include files:
	out_stream.write("// Generated file: only edit in designated areas!\n")
	out_stream.write("#include <{0:t}_Local.h>\n".format(self))

	#FIXME: This #include should not be hard wired in!!!
	out_stream.write("#include <MB7.h>\n")
	out_stream.write("\n")

	# Output a fenced region for top-level includes, typedef's, etc.:
	out_stream.write("// Put top level includes, typedef's here:\n")
	self.fence_write("TOP_LEVEL", out_stream)
	out_stream.write("\n")

	# Output the constructor with a fence in the middle:
	out_stream.write("// Constructor\n")
	out_stream.write("{0:t}::{0:t}(UByte address){1:b}".format(self, style))
	self.fence_write("CONSTRUCTOR", out_stream)
	out_stream.write("{0:e}\n".format(style))

	# Output the register access methods:
	for register in self.registers:
	    register.cpp_local_source_write(self, out_stream)

	# Output the function methods:
	for function in self.functions:
	    function.cpp_local_source_write(self, out_stream)

	# Wrap everything up:
	out_stream.close()

    ## @brief Write a C++ header for remote access to *self* out to *file-name*
    #  @param self *Module* to write C++ header information for.
    #  @param file_name

    # This method will write class definition file for *self*
    # for remote use (i.e. remote access via RPC.)  The class
    # definition is written to *file_name*. 
    def cpp_remote_header_write(self, file_name):

	assert isinstance(file_name, str)
	self.cpp_header_write(file_name, False)

    ## @brief Write C++ source file for RPC access to *self to *file_name*.
    #  @param self *Module* to write C++ source code for
    #  @param file_name *str* Name of file to write C++ code to
    #
    # This routine will write out a C++ source file that contains access
    # methods to use RPC to access remote functions and registers on
    # the remote module *self*.  The code is written out to the file
    # name *file_name*.

    def cpp_remote_source_write(self, file_name):

	# Check argument types:	
	assert isinstance(file_name, str)

	# Grab some values from *self*:
	style = self.style
	name = self.name

	# Now write out the new verision of *file_name* with the
	# edits from the previous file retained:
	out_stream = open(file_name, "w")

	# Output include files:
	out_stream.write("// Generated file!\n")
	out_stream.write("#include <{0}_Remote.h>\n".format(self.name))
	#KLUDGE:
	out_stream.write("#include <MB7.h>\n")
	out_stream.write("\n")

	# Output the constructor with a fence in the middle:
	out_stream.write("// {0} Constructor\n".format(name))
	out_stream.write("{0:t}::{0}(){1:b}".format(self, style))
	out_stream.write("{0:e}\n".format(style))

	# Output the register access methods:
	for register in self.registers:
	    register.cpp_remote_source_write(self, out_stream)

	# Output the function methods:
	for function in self.functions:
	    function.cpp_remote_source_write(self, out_stream)

	# Wrap everything up:
	out_stream.close()

    ## @brief Write "slave" C++ to support RPC's for *self* out to *file_name*.
    #  @param self *Module* for write C++ code for
    #  @param offset *int* offset where to start case statements
    #  @param out_stream *file* File to output case statements to
    #  @result *int* Offset for next batch of case statemetns
    #
    # This method will write out a C++ the case statements needed to
    # for all the registers and functions of *self*.  

    def ino_slave_write(self, offset, variable_name, out_stream):

	original_offset = offset
	#print "=>Module.ino_slave_write({0}, {1}, *)". \
	#  format(offset, variable_name)

	# Check argument types:
	assert isinstance(offset, int)
	assert isinstance(variable_name, str)
	assert isinstance(out_stream, file)

	# Grab some values from *self*:
	functions = self.functions
	name = self.name
	registers = self.registers
	style = self.style

	# Iterate over all *registers*:
	last_number = -1
	for register in registers:
	    register.ino_slave_write(offset, variable_name, out_stream)
	    if register.number > last_number:
		last_number = register.number + 1

	# Iterate over all *functions*:
	for function in functions:
	    function.ino_slave_write(offset, variable_name, out_stream)
	    if function.number > last_number:
		last_number = function.number

	offset += last_number + 1

	#print "<=Module.ino_slave_write({0}, {1}, *)=>{2}". \
	#  format(original_offset, variable_name, offset)

	return offset

    ## @brief Read in the fenced code for *file_name* into a table of *self*
    #  @param self *Module* that contains the fences table
    #  @param file_name *str* file name of the file to be read
    #
    # A this method will read in all of the fenced code for the file
    # named *file_name* into a fences table for *self*.  A fence is
    # user supplied code that is spliced into a file of computer 
    # generated code.  A fence looks as follows:
    #
    #          //////// Edit begins here: {FENCE_NAME}
    #          ...
    #          //////// Edit ends here: {FENCE_NAME}
    #
    # where "..." is zero, one or more lines of user supplied code.
    # This code reads in the "..." for each fence and hangs onto it
    # for subsequent out during code generation.

    def fences_read(self, file_name):

	# Check argument types:
	assert isinstance(file_name, str)

	# Grab some values from *self*:
        fences = {}

	# Does *file_name* already exist:
	if os.path.isfile(file_name):
            # Yes: read the entire contents in to memory as a line list:
	    in_stream = open(file_name, "r")
	    lines = in_stream.readlines()
	    in_stream.close()

	    # Now save a backup copy:
            out_stream = open(file_name + "~", "w")
            out_stream.writelines(lines)
	    out_stream.close()

	    # Now extact the user supplied file modications using regular
	    # expressions to find them:
	    fence_begin = self.fence_begin
	    fence_end = self.fence_end
	    fence_begin_pattern = re.compile(fence_begin)
	    fence_end_pattern = re.compile(fence_end)
	    fence_name_pattern = re.compile(r" (\w+)\n$")

	    # Start scaning through the lines:
	    fence_name = None
	    retained_lines = []
	    retain_lines = False
	    for line in lines:
		if fence_begin_pattern.match(line):
		    # We found a fence beginning:
		    fence_match = fence_name_pattern.search(line)
		    if fence_match != None:
			fence_name = fence_match.group(1)
		    #print "fence_name='{0}' '{1}'".format(fence_name, line)
		    retain_lines = True
		elif fence_end_pattern.match(line):
                    # The fence end has been found; save the current
		    # lines away:
		    fences[fence_name] = retained_lines

		    # Reset everything for the next fence:
                    retain_lines = False
		    retained_lines = []
		    fence_name = None
		elif retain_lines:
		    # Retain this line:
		    retained_lines.append(line)

	# Hang onto the retained chunks:
	self.fences = fences

    ## @brief Write fenced code for *fence_name* from *self* to *out_stream*
    #  @param self *Module* object that contains fenced code table
    #  @param fence_name *str* Name of fence to write out
    #  @param out_stream *file* file output stream that is open for writing
    #
    # A this method will write out the fenced code for *fence_name* out
    # to *out_stream* using the fences table in *self*.  A fence is
    # user supplied code that is spliced into a file of computer 
    # generated code.  A fence looks as follows:
    #
    #          //////// Edit begins here: {FENCE_NAME}
    #          ...
    #          //////// Edit ends here: {FENCE_NAME}
    #
    # where "..." is zero, one or more lines of user supplied code.
    # This code is read from *file_name prior to overwriting the file
    # with newly generated code.

    def fence_write(self, fence_name, out_stream):

	# Check argument types:
	assert isinstance(fence_name, str)
	assert isinstance(out_stream, file)

	# Output: "//////// Edit begins here: {FENCE_NAME}"
	out_stream.write("{0} {1}\n".format(self.fence_begin, fence_name))

	# Write out any fenced code that was previously read in:
	fences = self.fences
	if fence_name in fences:
	    out_stream.writelines(fences[fence_name])

	# Output "//////// Edit ends here: {FENCE_NAME}"
	out_stream.write("{0} {1}\n".format(self.fence_end, fence_name))

    ## @brief Collect the information needed for sketch generation.
    #  @param self *Module* to collect infromation from
    #  @param module_use *Module_Use* that referenced *self*
    #  @param sketch_generator *Sketch_Generator* to collect information into
    #  @param ident *int* amount to indent debug trace information by
    # 
    # This routine will collect the information needed to generate the
    # Arduino(tm) sketch code need for *self* using *sketch_generator*
    # to collect the sketch information into.  *indent* is used for
    # debugging to specify amount to indent tracing messages by.

    def sketch_generate(self, module_use, sketch_generator, indent):

        # Check argument types:
	assert isinstance(sketch_generator, Sketch_Generator)
	assert isinstance(indent, int)

	name = self.name
	vendor = self.vendor
	#print "{0}=>Module.sketch_generator({1}, {2})". \
	#  format(" " * indent, vendor, name)

	functions = self.functions
	registers = self.registers
	if len(functions) != 0 or len(registers) != 0:
	    # We need this module:
	    key = (vendor, name)
	    unique_modules = sketch_generator.unique_modules
	    if key in unique_modules:
		unique_modules[key].append(module_use)
	    else:
		unique_modules[key] = [ module_use ]

	#print "{0}<=Module.sketch_generator({1}, {2})". \
	#  format(" " * indent, vendor, name)

    ## @brief Write out Python RPC access code for *self* to *file_name*
    #  @param self *Module* to write Python code for
    #  @param file_name *str* file name to write Python code into
    #
    # This method will write out Python access code for *self* out to
    # the file named *file_name*.

    def python_write(self, file_name):

	# Check argument types:
	assert isinstance(file_name, str)

	# Grab some values from *self*:
	functions = self.functions
	name = self.name
	registers = self.registers
	style = self.style

	out_stream = open(file_name, "w")

	# Output the imports:
	out_stream.write("from Maker_Bus import *\n")
	out_stream.write("\n")

	# Output the class:
	out_stream.write("class {0} (Maker_Bus_Module):\n\n".format(name))
	style.indent_adjust(1)

	# Output the initializer:
	out_stream.write("{0:i}def __init__(self, maker_bus, address):\n". \
	  format(style))
	style.indent_adjust(1)
	out_stream.write( \
	  "{0:i}Maker_Bus_Module.__init__(self, maker_bus, address)\n".
	  format(style))
	style.indent_adjust(-1)
	out_stream.write("\n")

	# Output all the register member functions:
	for register in registers:
	    register.python_write(out_stream)

	# Output all the function member functions:
	for function in functions:
	    function.python_write(out_stream)

	# All done:
	style.indent_adjust(-1)
	out_stream.close()

# Not used any more:
#
# # @class Modules
#
# A list of Modules
#
# This class simply contains a list of *Module* objects that have
# been read from the modules "database".
#
#class Modules(Node):
#    """ Modules: ... """
#
#    ## @brief Initialize a list of modules.
#
#    def __init__(self, sub_nodes):
#	Node.__init__(self, "Modules", "Modules", None, sub_nodes, self.style)
#
#    def lookup(self, vendor, module_name):
#	print "lookup(vendor='{0}', module_name='{1}')". \
#	  format(vendor, module_name)
#	for module in self.sub_nodes:
#	    print "module:{0}".format(module.name)
#	    if module.name == module_name:
#		print "match"
#		return module
#	return None

## @class Module_Use
#
# One use of a Module
#
# This class represents one usage of a Module in a project.  A project
# can contain multiple instances of the same kind of module.

class Module_Use(Node):

    ## @brief Module_Use constructor
    #  @param self *Module_Use* to initialize
    #  @param name_vendor_module *None* or *tuple* of (name, vendor, module)
    #  @param module_uses *None* or *list* of module uses
    #  @param module_use_element *None* or *ET.Element* to read XML from
    #  @param modules_table *None* or *dict* Table of *Modules*
    #  @param style *Style* object that specifies how to format generate code.
    #
    # This method will initialize *self* from either *name_vendor_module*
    # looked up from *module_uses* or extract the information from
    # *module_use_element*

    def __init__(self, name_vendor_module, module_uses,
      module_use_element, modules_table, style):

	# Check argument types:
	assert name_vendor_module == None or \
	  isinstance(name_vendor_module, tuple)
	assert module_uses == None or isinstance(module_uses, list)
	assert module_use_element == None or \
	  isinstance(module_use_element, ET.Element)
	assert modules_table == None or isinstance(modules_table, dict)
	assert isinstance(style, Style)

	# Make sure that *module_uses* is a list:
	if module_uses == None:
	    module_uses = []
	offset = 0
	address = ""
	uid = ""

	# Initialize from *module_use_element* if it is not *None*:
	if module_use_element != None:
	    # Extract the module name, vendor, and vendor module name:
	    attributes = module_use_element.attrib
	    name = attributes["Name"]
	    vendor = attributes["Vendor"]
	    module_name = attributes["Module"]
	    if "Address" in attributes:
		address = attributes["Address"]
	    if "Offset" in attributes:
		offset = int(attributes["Offset"])
	    if "UID" in attributes:
		uid = attributes["UID"]

	    # Extract all of the sub Module_Use's:
	    for sub_module_use_element in \
	      module_use_element.findall("Module_Use"):
		module_use = Module_Use(None, None,
		  sub_module_use_element, modules_table, style)
		module_uses.append(module_use)
	elif name_vendor_module != None:
	    # Other wise initialize from *name_vendor_module*:
	    #print "name_vendor_module=", name_vendor_module
	    name = name_vendor_module[0]
	    vendor = name_vendor_module[1]
	    module_name = name_vendor_module[2]
	else:
	    # Must provide either a triple or an element:
	    assert False

	# Load up *self*:
	self.address = address
	self.offset = offset
	self.module_name = module_name
	self.module_uses = module_uses
	self.name = name
	self.style = style
	self.uid = uid
	self.vendor = vendor

	# Initialize *Node* base class:
	tree_text = "{0}".format(name, vendor, module_name)
	Node.__init__(self, "Module_Use", tree_text, None, module_uses, style)

    ## @brief Generate sketch code for *self* to *out_stream*.
    #  @param self *self* *Module_Use* to generate code for
    #  @param offset *int* Base offset for case statement
    #  @param module *Module* associated with *self*
    #  @param out_stream *file* to output to
    #  @result *offset* that has been updated
    #
    # This method will output the case statements needed for the
    # Arduino(tm) slave module for *self* out to *out_stream*.

    def ino_slave_write(self, offset, module, out_stream):

	original_offset = offset
	#print "=>Module_Use.ino_slave_write({0}, {1}, {2}, *)". \
	#  format(self.name, offset, module.name)

	# Check argument types:
	assert isinstance(offset, int)
	assert isinstance(module, Module)
	assert isinstance(out_stream, file)

	style = module.style
	out_stream.write("{0:i}// {1}\n".format(style, self.name))
        
	offset = module.ino_slave_write(offset, self.name, out_stream)

	out_stream.write("\n")

	#print "<=Module_Use.ino_slave_write({0}, {1}, {2}, *) => {3}". \
	#  format(self.name, original_offset, module.name, offset)

	return offset

    ## @brief Generate a sketch for *self* using *sketch_generator*
    #  @param self *Module_Use* 
    #  @param sketch_generator *Sketch_Generator* used to collect information
    #  @param indent *int* The amount to indent by for debugging
    #
    # This method will generate an Arduino(tm) sketch for *self* using
    # *sketch_generator* to collect all the information needed for the
    # sketch.  *indent* is used for debugging only and specifies the
    # amount to indent trace information by.

    def sketch_generate(self, sketch_generator, indent):

	#print "{0}=>Module_Use.sketch_generate()".format(" " * indent)

	# Check arguement types:
	assert isinstance(sketch_generator, Sketch_Generator)

	modules_table = sketch_generator.modules_table
	module = self.module_lookup(modules_table)
	module.sketch_generate(self, sketch_generator, indent + 1)

	for sub_module_use in self.module_uses:
	    sub_module_use.sketch_generate(sketch_generator, indent + 1)

	#print "{0}<=Module_Use.sketch_generate()".format(" " * indent)

    ## @brief Look up *Module* associated with *self* from *modules_table*
    #  @param self *Module_Use* to use
    #  @param modules_table *dict* Modules table keyed by (vendor, module_name)
    #  @result *Module* that corresponds to *self*
    #
    # This method will return the *Module* associated with *self* using
    # *modules_table*.  If no corresponding *Module* is found, *None* is
    # returned.

    def module_lookup(self, modules_table):

	# Check argument types:
	assert isinstance(modules_table, dict)
	
	# Perform the lookup:
	module = None
	key = (self.vendor, self.module_name)
	if key in modules_table:
	    module = modules_table[key]
            assert isinstance(module, Module)
	return module

    ## @brief Insert *new_node* into the module uses list for *self* at *index*
    #  @param self *Module_Use* to modify
    #  @param index *int* location to insert *new_node* into
    #  @param new_node *Node* base class object to insert into *self*
    #
    # This method will insert *new_node* into the module uses list of *self*
    # at the *index*'th slot.  *new_node* must be an object that uses
    # *Node* as its base class.

    def sub_node_insert(self, index, new_node):

	# Check argument types:
	assert isinstance(index, int)
	assert isinstance(new_node, Node)

	# Perform the insert:
	self.module_uses.insert(index, new_node)

    ## @brief Delete the *index*'th module use from *self*
    #  @param self "Module_Use* to modify
    #  @param index *int* Index slot of module use to delete
    #
    # This method will delete the *index*'th module use from *self*

    def sub_node_delete(self, index):

	# Check argument types:
	assert isinstance(index, int)

	# Perform the deletion:
	del self.module_uses[index]

    ## @brief Write XML of *self* to *out_stream* indented by *indent*.
    #  @param self *Module_Use* to write out
    #  @param indent *int* The amount to indent it by
    #  @param out_stream *file* to write the XML out to
    #
    # This method will write *self* in XML format to *out_stream* indented
    # by *indent*.

    def xml_write(self, indent, out_stream):
	
	# Check argument types:
	assert isinstance(indent, int)
	assert isinstance(out_stream, file)

	# Output the opening <Module_Use...>:
	out_stream.write("{0}<Module_Use".format("  " * indent))
	out_stream.write(' Name="{0}"'.format(self.name))
	out_stream.write(' Address="{0}"\n'.format(self.address))
	out_stream.write(' Offset="{0}"\n'.format(self.offset))
	out_stream.write(' UID="{0}"\n'.format(self.uid))
	out_stream.write('{0} Vendor="{1}"'.format("  " * indent, self.vendor))
	out_stream.write(' Module="{0}"'.format(self.module_name))

	# Output the nested *module_uses*:
	module_uses = self.module_uses
	if module_uses == None or len(module_uses) == 0:
	    # No nested *module_uses*.  Close off with "... />"
	    out_stream.write(" />\n")
	else:
	    # Close off "<Module_Use ...>\n":
	    out_stream.write(">\n")

            # Output the nested *module_uses*:
	    for module_use in module_uses:
		if isinstance(module_use, Module_Use):
		    module_use.xml_write(indent + 1, out_stream)

	    # Output the closing </Module_Use>:
	    out_stream.write("{0}</Module_Use>\n".format("  " * indent))

## @class Sketch_Generator
#
# Helper class for sketch generation.
#
# This class keeps track of the information needed to generate an Arduino(tm)
# sketch.

class Sketch_Generator:

    ## @brief Sketch_Generate constructor
    #  @param self *Sketch_Generator* to initialize
    #  @param name *str* Name of module being generated
    #  @param modules_table *dict* Modules table keyed by (vendor, module_name)
    #  @param style *Style* object to control generated code formatting.
    #
    # This method will initialize *self* with both *name* and *modules_table*
    # looked up from *module_uses* or extract the information from
    # *module_use_element*

    def __init__(self, name, modules_table, style):

	# Check argument types:
	assert isinstance(name, str)

	# Load up *self*:
	self.name = name
	self.modules_table = modules_table
	self.style = style
	self.unique_modules = {}

    #  @result *bool* *True* if any *Module_Use* offset is changed.

    def write(self, root_module_use):
	modules_table = self.modules_table
	unique_modules = self.unique_modules

	for module_key in unique_modules:
	    #print "module_key=", module_key
	    module = modules_table[module_key]
	    name = module.name
            vendor = module.vendor

	    path = module.path
	    #print "path={0}".format(path)
	    directory = os.path.dirname(path)
	    #print "directory={0}".format(directory)
	    libraries_directory = os.path.join(directory, "libraries")
	    if not os.path.isdir(libraries_directory):
		# Create *libraries_directory*:
		os.makedirs(libraries_directory)
		
	    local_library_directory = \
	      os.path.join(libraries_directory, "{0:t}_Local".format(module))
	    #print "local_library_directory={0}".format(local_library_directory)
            if not os.path.isdir(local_library_directory):
		# Create *local_library_directory*:
		os.makedirs(local_library_directory)

	    remote_library_directory = \
	      os.path.join(libraries_directory, "{0:t}_Remote".format(module))
	    #print "remote_library_directory={0}". \
	    #  format(remote_library_directory)
	    if not os.path.isdir(remote_library_directory):
		# Create *remote_library_directory*:
		os.makedirs(remote_library_directory)

	    sketchbook_libraries_directory = \
	      os.path.join("sketchbook", "libraries")
	    if not os.path.isdir(sketchbook_libraries_directory):
		# Create *sketchbook_libraries_directory*:
		os.makedirs(sketchbook_libraries_directory)

	    sketchbook_local_library_directory = \
	      os.path.join(sketchbook_libraries_directory,
	      "{0:t}_Local".format(module))
	    #FIXME: Relative stuff is hardwired!!!:
	    sketchbook_relative_local_library_directory = \
	      os.path.join("..", "..", "..",
	      "configurator", local_library_directory)
	    #print "srlld:{0}\nslld:{1}". \
	    #  format(sketchbook_relative_local_library_directory,
	    #  sketchbook_local_library_directory)
	    if os.path.exists(sketchbook_local_library_directory):
	    	os.remove(sketchbook_local_library_directory);
	    os.symlink(sketchbook_relative_local_library_directory,
	      sketchbook_local_library_directory)

	    local_header_file = os.path.join(local_library_directory,
	      "{0:t}_Local.h".format(module))
	    module.cpp_header_write(local_header_file, True)

	    local_cpp_file = os.path.join(local_library_directory,
	      "{0:t}_Local.cpp".format(module))
	    module.cpp_local_source_write(local_cpp_file)

	slave_directory = \
	  os.path.join("sketchbook", "{0}_Slave".format(self.name))
	#print "slave_directory={0}".format(slave_directory)
	if not os.path.exists(slave_directory):
	    os.makedirs(slave_directory)

	slave_ino_source = \
	  os.path.join(slave_directory, "{0}_Slave.ino".format(self.name))

	# Set *debug* to *True* to force debugging code to be generated:
	debug = True
	    
	#print "slave_ino_source={0}".format(slave_ino_source)
	out_stream = open(slave_ino_source, "w")

	# Output the #includes:
	out_stream.write("// #includes:\n")
	out_stream.write("#include \"MB7.h\"\n")
	for module_key in unique_modules:
	    #print "module_key=", module_key
	    module = modules_table[module_key]
	    out_stream.write("#include <{0:t}_Local.h>\n".format(module))
	out_stream.write("\n")

	# Output one object variable per *module_use*:
	out_stream.write("// Object variables:\n")
	out_stream.write("Maker_Bus maker_bus;\n")
	for module_key in unique_modules:
	    #print "module_key=", module_key
	    module = modules_table[module_key]

	    module_uses = unique_modules[module_key]
            for module_use in module_uses:
		out_stream.write("{0:t} {1}({2});\n". \
		  format(module, module_use.name, module_use.address))
	out_stream.write("\n")

	# Output command_process() declaration:
	out_stream.write("// Forward declaration of command_process():\n")
	out_stream.write("UByte command_process(const Maker_Bus *maker_bus,\n")
	out_stream.write(" UByte command, Logical execute_mode);\n")
	out_stream.write("\n")

	# Output the setup() routine:
	style = self.style
	out_stream.write("void setup(){0:b}".format(style))

	if debug:
	    out_stream.write("{0:i}Serial.begin(9600);\n".format(style))
	    out_stream.write('{0:i}Serial.print("\\n{1}:\\n");\n'. \
	      format(style, self.name))

	out_stream.write("{0:e}\n\n".format(style))

	# Output the loop() routine:
	out_stream.write("void loop(){0:b}".format(style))
	out_stream.write( \
	  "{0:i}maker_bus.slave_mode({1}, command_process);\n". \
	  format(style, root_module_use.address))
	out_stream.write("{0:e}\n\n".format(style))

	# Output the command processor routine:
	out_stream.write("UByte command_process(Maker_Bus *maker_bus, " + \
	  "UByte command, Logical execute_mode){0:b}".format(style))
	out_stream.write("{0:i}switch (command){0:b}".format(style))

	# Output access code for each *module_use*:
	modified = False
	offset = 0
	for module_key in unique_modules:
	    #print "module_key=", module_key
	    module = modules_table[module_key]

	    module_uses = unique_modules[module_key]
            for module_use in module_uses:
		#print "B:mod.name={0} mod.off={1} offset={2} modified={3}". \
		#  format(module_use.name, module_use.offset, offset, modified)
		if module_use.offset != offset:
		    module_use.offset = offset
		    modified = True		    
		#print "A:mod.name={0} mod.off={1} offset={2} modified={3}". \
		#  format(module_use.name, module_use.offset, offset, modified)

		offset = module_use.ino_slave_write(offset, module, out_stream)

	# Close off the command proccessor routine:
	out_stream.write("{0:e}".format(style))
	out_stream.write("{0:i}return 0;\n".format(style))
	out_stream.write("{0:e}".format(style))

	# Close *out_stream*:
	out_stream.close()

	#print "modified={0}".format(modified)
	return modified

## @class Overview
#
# Overview description of a Module
#
# This class captures the overview text for a module.  It corresponds
# to the following XML:
#
#        <Overview>
#          Overview text goes here.
#        </Overview>

class Overview:

    ## @brief Initialize *self* from XML in *overview_element*.
    #  @param self *Overview* to fill from *overview_element*.
    #  @param overview_element *ET.Element* to extract XML from
    #  @param style *Style* object that specifies how to format generate code.
    #
    # This method will initialize *self* with the Overview XML tag contained
    # in *overview_element*.

    def __init__(self, overview_element, style):

	# Check argument types:
	assert isinstance(overview_element, ET.Element)
	assert overview_element.tag == "Overview"
	assert isinstance(style, Style)

	# Load up *self*
	self.style = style
	self.text = overview_element.text

    ## @brief Extract and return *Overview* object from *parent_element*.
    #  @param parent_element *ET.Element* that contains Overview XML
    #  @param style *Style* object that specifies how to format generate code.
    #  @result *Overview* object that extracted is returned.
    # 
    # This static method will extract the XML Overview tag from
    # *parent_element* and return it.

    @staticmethod
    def extract(parent_element, style):

	# Check argument types:
	assert isinstance(parent_element, ET.Element)
	assert isinstance(style, Style)

	# Extract all <Overview> tags:
	overviews = []
	for overview_element in parent_element.findall("Overview"):
	    overviews.append(Overview(overview_element, style))

	# Now make sure we got exactly one:
	overview = None
	if len(overviews) == 1:
	    overview = overviews[0]
	else:
	    print "{0}:<{1} Name='{2}'...> has {3} <Overview> tags". \
	      format(XML.line_number(parent_element), 
		parent.tag, parent.attrib["Name"], len(overviews))

	return overview

## @class Parameter
#
# One function Parameter
#
# This class corresponds to a one function parameter.  It corrsponds
# to the following XML:
#
#        <Parameter Name="..." Type="..." Brief="...">

class Parameter:

    ## @brief Initialize *self* from the XML in *parameter_element*.
    #  @param self *Parameter* to initialize
    #  @param parameter_element *ET.Element* to extract XML from
    #  @param style *Style* object that specifies how to format generate code.
    #
    # This method will initialize *self* from the XML in *parameter_element*.

    def __init__(self, parameter_element, style):

	# Check argument types:
	assert isinstance(parameter_element, ET.Element)
	assert parameter_element.tag == "Parameter"
	assert isinstance(style, Style)

	# Load up *self*:
	attributes = parameter_element.attrib
	self.brief = attributes["Brief"]
	self.name = attributes["Name"]
	self.style = style
	self.type = attributes["Type"]

    ## @brief Return a formated string for *self* using *fmt* for format control
    #  @param self *Parameter* to format
    #  @param fmt *str* that contains format control information
    #
    # This method will format *self* using *fmt* for format control.  *fmt*
    # must be one of the following:
    #
    #  * 't' return the type of *self*
    #  * 'n' return the name of *self*
    #  * 'c' return the C/C++ type of *self* (i.e. "Type Name")

    def __format__(self, fmt):

	if fmt == "t":
	    result = self.type
        elif fmt == "n":
	    result = self.name
	elif fmt == "c":
	    result = self.type + " " + self.name
	else:
	    result = "@Parameter:{0}@".format(fmt)
	return result

## @class Project
#
# A Project configuration
#
# This class specifies the overall configuration of a project.
# It corresponds to the following XML:
#
#        <Project Name="...">
#          <Module_Use Name="..." Vendor="..." Module="...">
#            ...
#          </Module_Use>
#        </Project>

class Project(Node):

    ## @brief Initialize *self* from XML in *project_element*.
    #  @param self *Project* to initialize
    #  @param project_element *None* *ET.Element* that contains the XML
    #  @param modules_table *dict* module look up table
    #  @param style *Style* object that specifies how to format generate code.
    #
    # This method will initialize *self* from the XML in project_element.
    # *modules_table* is used to construct a table of the *modules* that
    # are read in.  If *project_element* is *None*, a *self* is initialized
    # to an empty project.

    def __init__(self, project_element, modules_table, style):

	# Check argument types:
	assert project_element == None or \
	  isinstance(project_element, ET.Element)
	assert isinstance(modules_table, dict)
	assert isinstance(style, Style)

	# Dispatch on whether *project_element* is empty or not
	module_uses = []
	if project_element == None:
	    # Just create an empty project:
	    name = "my_project"
	else:
            # Extract <Project> tag from *project_element*:
	    attributes = project_element.attrib

	    # Grab the name attribute:
	    name = attributes["Name"]

	    # Extract all of the Module_Use's:
	    for module_use_element in project_element.findall("Module_Use"):
		module_use = Module_Use(None,
		  None, module_use_element, modules_table, style)
	    module_uses.append(module_use)

	# Save away *name* and *module_uses*:
	self.name = name
	self.module_uses = module_uses

	# Initialize the *Node* base class:
	Node.__init__(self, "Project", "Project", None, module_uses, style)

    ## @brief Delete the *index*'th sub node from *self
    #  @param self *Project* to delete sub node from
    #  @param index *int* The index of the sub node to delete
    #
    # This method will delete the *index*'th sub node of *self*.

    def sub_node_delete(self, index):

	# Check argument types:
	assert isinstance(index, int)

	# Perform the deletion:
	del self.module_uses[index]

    ## @brief Write *self* out as XML to *out_stream* indented by *indent*
    #  @param self *Project* to write out as XML
    #  @param indent *int* The amount to indent the XML by
    #  @param out_stream *file* to write XML out to
    #
    # This method will write *self* out as XML to *out_stream* indented
    # by *indent*.  Currently, *indent* must be 0.

    def xml_write(self, indent, out_stream):

        # Check argument types:
	assert isinstance(indent, int)
	assert indent == 0
	assert isinstance(out_stream, file)

	# Output the <Project ... > tag:
	out_stream.write('<Project Name="{0}">\n'.format(self.name))
	
	# Output all the module uses:
	module_uses = self.module_uses
	for module_use in module_uses:
	    module_use.xml_write(indent + 1, out_stream)

	# Output the </Project> tag:
	out_stream.write('</Project>\n')
	
## @class Register
#
# A module Register.
#
# A register represents a single register that is accessible via
# remote procedure call.  It corresponds as the following XML:
#
#        <Register Name="..." Type="..." Number="..." Brief="...">
#        <Description>
#          *Description goes here*
#        </Description>
#        </Register>

class Register(Node):

    def __init__(self, register_element, style):
	""" Register: Initialize self from *register_element*. """

	assert register_element.tag == "Register", "Need a register element"

	attributes = register_element.attrib

	name = attributes["Name"]
	type = attributes["Type"]

	self.brief = attributes["Brief"]
	self.description = Description.extract(register_element, style)
	self.name = name
	self.number = int(attributes["Number"])
	self.type = type

	Node.__init__(self, "Register", name, None, None, style)

    def __format__(self, fmt):
	""" Register: Return a formatted version of *self* controlled by
	    *fmt*.
	    If *fmt* is a 'r', a routine name is returned.
	    If *fmt* is a 'g', a "get" routine name is returned.
	    if *fmt* is a 's', a "set" routine name is returned.
	    If *fmt* is a 't', the register type is returned.
	    If *fmt* is a 'n', the reigster name is returned.  """

	style = self.style
	if fmt == 'r':
	    result = style.routine_name(self.name)
	elif fmt == 'g':
	    result = style.routine_name(self.name + ' get')
	elif fmt == 's':
	    result = style.routine_name(self.name + ' set')
	elif fmt == 'n':
	    result = self.name 
	elif fmt == 't':
	    result = self.type
	else:
	    result = "@Register:{0}@".format(fmt)
	return result

    def cpp_header_write(self, module, out_stream):
	""" Register: Write out the register method declarations for
	    *self* to *out_stream*. """

	# Grab some values from *self}:
	name = self.name
	style = self.style

	# Output the brief comment:
	out_stream.write("{0:i}// {1}\n".format(style, self.brief))

	# Output the "get" method "Type {name}_get();":
	out_stream.write("{0:i}{1:t} {1:g}();\n".format(style, self))

	# Output the "set" method "void {name}_set(Type name)":
	out_stream.write("{0:i}void {1:s}({1:t} {1:n});\n\n". \
	  format(style, self))

    def cpp_local_source_write(self, module, out_stream):
	""" Register: This routine will write out the implemenation code
	    template for *self* to *out_stream* using *module* for
	    fenced code.  """

	# Grab some values from *self*:
	style = self.style
	name = self.name

	# Output the "get" method code.  It looks like this:
	#	// REGISTER_get: BRIEF
	#	TYPE MODULE::REGISTER_get() {
	#	   //////// Fence begin
	#	   //////// Fence end
	#	}

	# Output the brief comment:
	get_name = "{0:g}".format(self)
	out_stream.write("// {0}: {1}\n".format(get_name, self.brief))

	# Output the method signature:
	out_stream.write("{0:i}{1:t} {2:t}::{3}(){0:b}". \
	  format(style, self, module, get_name))

	# Output the code fence:
	module.fence_write(get_name.upper(), out_stream)

	# Output the closing brace:
	out_stream.write("{0:e}\n".format(style))

	# Output the "set" routine.  It looks as follows:
	#	// REGISTER_set: BRIEF
	#	void REGISTER_SET(TYPE NAME) {
	#	    //////// Fence begin
	#           //////// Fence end
	#	}

	# Output the brief comment:
	set_name = "{0:s}".format(self)
	out_stream.write("// {0}: {1}\n".format(set_name, self.brief))

	# Output the method signature:
	out_stream.write("{0:i}void {1:t}::{2}({3:t} {3:n}){0:b}". \
	  format(style, module, set_name, self))

	# Output the fence:
	module.fence_write(set_name.upper(), out_stream)

	# Output the closing brace:
	out_stream.write("{0:e}\n".format(style))

    def cpp_remote_source_write(self, module, out_stream):
	""" Register: This routine will write out the implemenation code
	    template for *self* to *out_stream* using *module* for
	    fenced code.  """

	# Grab some values from *self*:
	style = self.style
	name = self.name
	type = self.type
	number = self.number

	# Output the "get" method code.  It looks like this:
	#	// REGISTER_get: BRIEF
	#	TYPE MODULE::REGISTER_get() {
	#	    Maker_Bus_Module::command_begin(NUMBER);
	#	    TYPE NAME = Maker_Bus_Module::TYPE_get();
	#	    Maker_Bus_Module::command_end();
	#	    return NAME;
	#	}

	# Output the brief comment:
	get_name = "{0:g}".format(self)
	out_stream.write("// {0}: {1}\n".format(get_name, self.brief))

	# Output the method signature:
	out_stream.write("{0:i}{1:t} {2:t}::{3}(){0:b}". \
	  format(style, self, module, get_name))

	#	    Maker_Bus_Module::command_begin(NUMBER);
	out_stream.write("{0:i}Maker_Bus_Module::command_begin({1});\n". \
	  format(style, number))

	# Output: "TYPE NAME = Maker_Bus_Module::TYPE_get()";
	out_stream.write("{0:i}{1} {2} = Maker_Bus_Module::{3}_get();\n". \
	  format(style, type, name.lower(), type.lower()))

	# Output: "Maker_Bus_Module::command_end();"
	out_stream.write("{0:i}Maker_Bus_Module::command_end();\n". \
	  format(style))

	# Output: "return NAME;"
	out_stream.write("{0:i}return {1};\n".format(style, name.lower()))

	# Output the closing brace:
	out_stream.write("{0:e}\n".format(style))

	# Output the "set" routine.  It looks as follows:
	#	// REGISTER_set: BRIEF
	#	void REGISTER_SET(TYPE NAME) {
	#	    Maker_Bus_Module::command_begin(NUMBER + 1);
	#	    Maker_Bus_Module::TYPE_put(NAME);
	#	    Maker_Bus_Module::command_end();
	#	}

	# Output: "// REGISTER_set: BRIEF":
	set_name = "{0:s}".format(self)
	out_stream.write("// {0}: {1}\n".format(set_name, self.brief))

	# Output: "void REGISTER_SET(TYPE NAME) {"
	out_stream.write("{0:i}void {1:t}::{2}({3:t} {3:n}){0:b}". \
	  format(style, module, set_name, self))

	# Output: Maker_Bus_Module::command_begin(NUMBER + 1);
	out_stream.write("{0:i}Maker_Bus_Module::command_begin({1});\n". \
	  format(style, number + 1))
	
	# Output: Maker_Bus_Module::TYPE_set(NAME);
	out_stream.write("{0:i}Maker_Bus_Module::{1}_put({2});\n". \
	  format(style, type.lower(), name.lower()))

	# Output: Maker_Bus_Module::command_end();
	out_stream.write("{0:i}Maker_Bus_Module::command_end();\n". \
	  format(style))

	# Output the closing brace:
	out_stream.write("{0:e}\n".format(style))

    def ino_slave_write(self, offset, module_name, stream):
	""" Register: Write C++ code for *self* to *stream* where
	    the code is a case clause of a switch statement that
	    processes a remote procedure call. """

	assert isinstance(offset, int)
	assert isinstance(module_name, str)
	assert isinstance(stream, file)

	# Grab some values out of *self*:
	brief = self.brief
	name = self.name
	number = self.number
	style = self.style
	type = self.type

	write = stream.write
	# Output the code for the get method:
	stream.write("{0:i}case {1}:{0:b}".format(style, offset + number))
	stream.write("{0:i}// {1:g}: {2}\n".format(style, self, brief))
	stream.write("{0:i}if (execute_mode){0:b}".format(style))
	stream.write("{0:i}{1} {2} = {3}.{4:g}();\n". \
	  format(style, type, name, module_name.lower(), self))
	stream.write("{0:i}maker_bus->{1}_put({2});\n". \
	  format(style, type.lower(), name))
	stream.write("{0:e}".format(style))
	stream.write("{0:i}break;\n".format(style))
	stream.write("{0:e}".format(style))

	# Output the case for the set method:
	stream.write("{0:i}case {1}:{0:b}".format(style, offset + number + 1))
	stream.write("{0:i}// {1:s}: {2}\n".format(style, self, brief))
	stream.write("{0:i}if (execute_mode){0:b}".format(style))
	stream.write("{0:i}{1} {2} = maker_bus->{3}_get();\n". \
	  format(style, type, name, type.lower()))
	stream.write("{0:i}{1}.{2:s}({2:n});\n". \
	  format(style, module_name.lower(), self))
	stream.write("{0:e}".format(style))
	stream.write("{0:i}break;\n".format(style))
	stream.write("{0:e}".format(style))

    def python_write(self, out_stream):
	""" Register: Write the python method functions for *self* to
	    *out_stream*.  This is both a "get" and a "set" method
	    function. """

	brief = self.brief
	name = self.name
	number = self.number
	style = self.style
	type = self.type

	# Output a register "get" method that looks as follows:
	#
	#	def REGISTER_get(self):
	#	    // Get: BRIEF
	#
	#	    self.request_begin(NUMBER)
	#	    self.request_end()
	#	    return self.response_TYPE_get()

	# Output "def REGISTER_get(self):":
	out_stream.write("{0:i}def {1:g}(self):\n".format(style, self))

	# Indent code body:
	style.indent_adjust(1)

	# Output: "// Get: BRIEF"
	out_stream.write("{0:i}# Get: {1}\n\n".format(style, brief))

	# Output: "self.request_begin(NUMBER)"
	out_stream.write("{0:i}self.request_begin({1})\n".format(style, number))

	# Output: "self.request_end()"
	out_stream.write("{0:i}self.request_end()\n".format(style))

	# Output: "return self.response_TYPE_get()"
	out_stream.write("{0:i}return self.response_{1}_get()\n\n". \
	      format(style, type.lower()))

	# Restore indentation:
	style.indent_adjust(-1)

	# Output a register "set" method looks as follows:
	#
	#	def REGISTER_set(self, REGISTER):
	#	    // Set: BRIEF
	#
	#	    self.request_begin(NUMBER + 1)
	#	    self.request_TYPE_put(REGISTER)
	#	    self.request_end()

	# Output: "def REGISTER_set(REGISTER):":
	out_stream.write("{0:i}def {1:s}(self, {1:n}):\n".format(style, self))

	style.indent_adjust(1)

	# Output: "// Set: BRIEF"
	out_stream.write("{0:i}# Set: {1}\n\n".format(style, brief))

	# Output: "self.request_begin(NUMBER + 1)"
	out_stream.write("{0:i}self.request_begin({1})\n". \
	  format(style, number + 1))

	# Output: "self.request_TYPE_put(REGISTER)"
	out_stream.write("{0:i}self.response_{1}_set({2:n})\n". \
	      format(style, type.lower(), self))

	# Output: "self.request_end()"
	out_stream.write("{0:i}self.request_end()\n\n".format(style))

	# Restore indentation:
	style.indent_adjust(-1)

## @class Result
#
# One function Result
#
# This class represents one result from a function.  It corresponds
# to the following XML:
#
#        <Result Name="..." Type="..." Brief="..." />

class Result:
    """ Result: This class represents a function result. """

    def __init__(self, result_element, style):
	""" Result: Initialize *self* from *result_element*. """

	assert result_element.tag == "Result", "Need a <Result ...> element"

	attributes = result_element.attrib

	self.brief = attributes["Brief"]
	self.name = attributes["Name"]
	self.style = style
	self.type = attributes["Type"]

    def __format__(self, fmt):
	""" Result: Return a formatted version of *self*
	    controlled by *fmt*.
	    If *fmt* is a 't', return the type of *self*.
	    If *fmt* is a 'n', return the name of *self*.
	    If *fmt* is a 'c', return a C/C++ typed name.  """

	if fmt == 't':
	    result = self.type
        elif fmt == 'n':
	    result = self.name
	elif fmt == 'c':
	    result = self.type + " " + self.name
	else:
	    result = "@Result:{0}@".format(fmt)
	return result

## @class Selection
#
# One Selection from the selections tree.
#
# This class represents one *Node* in the selections tree the
# corresponds to the available modules that can be included in
# a module.  The selections tree is constructed as a side effect
# of read through the modules database.

class Selection(Node):

    def __init__(self, name, style):
	""" """

	sub_selections = []
	self.name = name
	self.sub_selections = sub_selections
	self.table = {}

	Node.__init__(self, "Selection", name, None, sub_selections, style)

    def lookup_or_create(self, name):
	table = self.table
	if name in table:
	    result = table[name]
	else:
	    result = Selection(name, self.style)
	    table[name] = result
	    self.sub_selections.append(result)
	return result

    def module_append(self, module):
	self.sub_selections.append(module)

    def sort(self):
	sub_selections = self.sub_selections
	sub_selections.sort(key=lambda sel: sel.name)
	for sub_selection in sub_selections:
	    if sub_selection.class_name == "Selection":
		sub_selection.sort()

## @class Style
#
# Output formatting Style
#
# This class contains all of the information that controls output
# formatting.  This is primarily used for controlling the look
# of generated C, C++, and Python code.

class Style:
    """ The Style class controls the output style of C, C++, Python, etc.  """

    def __init__(self, application):
	""" Style: Initialize *self* object. """

	self.application = application
	self.file_name = "<no_file>"
	self.indent = 0
	self.name_underscores = True

    def __format__(self, fmt):
	""" Style: Format *self* controlled by *fmt*.
	    If *fmt* is 'i', return the current indent string.
	    If *fmt* is 'b', return new block indent.
	    if *fmt* is 'e', return an end block indent.
	    if *fmt* is 'E', return an end block indent with a semicolon.
	    if *fmt* is 'f', return the current file name.  """

	if fmt == 'i':
	    result = "  " * self.indent
	elif fmt == 'b':
	    self.indent += 1
	    result = " {\n"
	elif fmt == 'e':
	    indent = self.indent - 1
	    self.indent = indent
            result = "  " * indent + "}\n"
	elif fmt == 'E':
	    indent = self.indent - 1
	    self.indent = indent
            result = "  " * indent + "};\n"
	elif fmt == 'f':
            result = self.file_name
	else:
	    result = "@Style:{0}@".format(fmt)
	return result

    def file_name_set(self, file_name):
	""" Style: Save current file name in *self*. """

	self.file_name = file_name

    def routine_name(self, name):
	""" Style: Return *name* in the style specified by *self*. """

	if self.name_underscores:
	    result_name = ""
	    words = name.split(" ")
	    prefix = ""
	    for word in words:
		result_name = result_name + prefix + word
		prefix = "_"
	else:
	    assert False
	return result_name

    def indent_adjust(self, adjust):
	""" Style: Return the appropriate amount of spaces to get
	    to *level* indenation as specified by *self*. """

	self.indent += adjust

## @class XML_Check
#
# A helper class to help check XML files for errors
#
# This class is used to provide a data structure that is used
# to check XML file structure.  It keeps track of allowable
# sub-tags, required attributes and optional attributes.

class XML_Check:
    """ This class lists the allowed child tags and attributes for a given
	tag name. """

    def __init__(self, name, has_text, tags):
	""" Initialize *self* to contain *name* and insert into *tags*. """

	self.name = name
	self.has_text = has_text
	self.child_tags = {}
	self.required_attributes = {}
	self.optional_attributes = {"LN": 0}
	tags[name] = self

    @staticmethod
    def tags_initialize():
	tags = {}

	classification = XML_Check("Classification", False, tags)
	classification.required_attribute("Level1")
	classification.optional_attribute("Level2")
	classification.optional_attribute("Level3")
	classification.optional_attribute("Level4")
	classification.optional_attribute("Level5")
	classification.optional_attribute("Level6")
	classification.optional_attribute("Level7")
	classification.optional_attribute("Level8")
	classification.child_tag("Classification")

	connector = XML_Check("Connector", False, tags)
	connector.required_attribute("Bus")
	connector.required_attribute("Name")
	connector.required_attribute("Physical_Connector")

	description = XML_Check("Description", True, tags)

	function = XML_Check("Function", False, tags)
	function.required_attribute("Name")
	function.required_attribute("Number")
	function.required_attribute("Brief")
	function.child_tag("Description")
	function.child_tag("Parameter")
	function.child_tag("Result")

	module = XML_Check("Module", False, tags)
	module.required_attribute("Name")
	module.required_attribute("Brief")
	module.required_attribute("Vendor")
	module.optional_attribute("Address_RE")
	module.optional_attribute("Generate")
	module.optional_attribute("Sub_Class")
	module.child_tag("Overview")
	module.child_tag("Connector")
	module.child_tag("Function")
	module.child_tag("Register")
	module.child_tag("Classification")

	module_use = XML_Check("Module_Use", True, tags)
	module_use.required_attribute("Name")
	module_use.required_attribute("Vendor")
	module_use.required_attribute("Module")
	module_use.optional_attribute("Address")
	module_use.optional_attribute("Address_RE")
	module_use.optional_attribute("Offset")
	module_use.optional_attribute("UID")
	module_use.child_tag("Module_Use")

	overview = XML_Check("Overview", True, tags)

	parameter = XML_Check("Parameter", False, tags)
	parameter.required_attribute("Name")
	parameter.required_attribute("Type")
	parameter.required_attribute("Brief")

	project = XML_Check("Project", True, tags)
	project.required_attribute("Name")
	project.child_tag("Module_Use")

	register = XML_Check("Register", False, tags)
	register.required_attribute("Name")
	register.required_attribute("Type")
	register.required_attribute("Number")
	register.required_attribute("Brief")
	register.child_tag("Description")

	result = XML_Check("Result", False, tags)
	result.required_attribute("Name")
	result.required_attribute("Type")
	result.required_attribute("Brief")

	return tags

    def child_tag(self, name):
	""" Append *name* as an allowed child tag for *self*. """

	self.child_tags[name] = 0

    def required_attribute(self, name):
	""" Append *name* as a requried attribute for *self*. """

	self.required_attributes[name] = 0

    def optional_attribute(self, name):
	""" Append *name* as an optional attribute for *self*. """

	self.optional_attributes[name] = 0

    def attributes_check(self, element):
	""" Check *element* to see if it has valid attributes as
	    specified by *self*. """

	element_attributes = element.attrib
	for attribute_name in element_attributes.keys():
            if not (attribute_name in self.required_attributes) and \
	      not (attribute_name in self.optional_attributes):
		print "{0}:<{1}...> does not permit {2} attribute". \
		  format(XML.line_number(element), element.tag, attribute_name)
	for attribute_name in self.required_attributes.keys():
	    if not (attribute_name in element_attributes):
		print "{0}:Tag <{1}...> requires {2} attribute". \
		  format(XML.line_number(element), element.tag, attribute_name)
	    
    @staticmethod
    def element_check(element, tags):
	""" Check *element* for consistency using the *XML_Check* objects
	    in the *tags* dictionary. """

	assert isinstance(element, ET.Element)
	assert isinstance(tags, dict)

	# Is *element* a valid tag name:
	if element.tag in tags:
	    xml_check = tags[element.tag]

	    xml_check.attributes_check(element)

	    # Visit element children:
	    for child in element:
		if child.tag in xml_check.child_tags:
		    XML_Check.element_check(child, tags)
		else:
		    print ("{0}:<{1}...> disallowed under <{2}...>"). \
		      format(XML.line_number(child), child.tag, element.tag)
	else:
	    print "{0}:<{0}...> is unknown". \
	      format(XML.line_number(element), element.tag)

## @class XML
#
# XML file processing
#
# This class encapsulates the code for processing XML files

class XML:

    def __init__(self, style):
	""" XML: Initialize *self*. """
	XML.style = style

    def file_name_set(self, file_name):
	self.file_name = file_name

    @staticmethod
    def line_number(element):
	""" This routine will return the line number associated
	    with {element}. """

	# Return 0 if no "LN" attribute is found:
	number = 0
	attributes = element.attrib
	if "LN" in attributes:
	    # We found it, use the attribute value instead:
	    number = attributes["LN"]
	return "{0:f}@{1}".format(XML.style, number)

    def read(self, file_name, module_name):
	""" This routine will read in *file_name* as an XML file and
	    return the top-most element.  The various tags of the XML
	    are modified to have an LN attribute that contains the
	    file line number on which the tag occurs. """

	# Read in the XML file as a list of lines:
	xml_file = open(file_name)
	xml_lines = xml_file.readlines()
	xml_file.close()

	# For error reporting, it is nice to know the line number of where
	# the error occurred.  Unfortunately, the ElementTree package does
	# not store parse position information in the Element object.  To
	# work around this situation, we sweep through each line that was
	# read in and append a line number attribute appropriate tags.
	# Thus, '<Module ...' becomes "<Module LN="#" ...' where # is the
	# actual line number.  When there is an error, the appropriate
	# line number is read out using element.attrib["LN"].  This is
	# wrapped up in the line_number() function, just in the unlikely
	# case a tag line number is missed.

	# This pattern will match the tag at the beginning of the line:
	pattern = re.compile("^[ \t]*<\w+")

	# Scan through each line:
	replaced_lines = []
	for index in range(len(xml_lines)):
	    # Fetch each line one at a time:
	    line = xml_lines[index]

	    # Do we have the tag at the beginning of the line?
	    match = pattern.search(line)
	    if match:
		# Yes!  It can only match once, so grab the tag text:
		tag_text = match.group(0)

		# Append the line number attribute to the tag text:
		tag_text += ' LN="{0}"'.format(index + 1)

		# Substitute it back into the line:
		line = pattern.sub(tag_text, line)
	    #print "{0}\t{1}".format(line_number, line)

	    # Build up the replaced lines list:
	    replaced_lines.append(line)

	# Now parse the modified XML lines into a top level element tree root:
	root_element = None

	# The commented code works for Python 2.7:
	#try:
	#    root_element = ET.fromstringlist(replaced_lines)
	#except ET.ParseError as e:
        #    print "'{0}': {1}".format(file_name, e)

	# This code works for Python 2.6:
	try:
	    root_element = ET.fromstring("".join(replaced_lines))
	except ET.ParseError as e:
            print "'{0}': {1}".format(file_name, e)

	if root_element != None:
	    root_tag = root_element.tag
	    if root_tag != module_name:
		print "'{0}:' does not start with <{1}...> tag.". \
		  format(file_name, root_tag)

	return root_element

# End of classes:

def main():
    style = Style()

    # Kludge:
    arduino_dir = "../arduino/"
    sketchbook_dir = arduino_dir + "sketchbook/"
    sketch_dir = sketchbook_dir + "MB7_Slave/"
    libraries_dir = sketchbook_dir + "libraries/"
    lcd32_local_dir = libraries_dir + "LCD32_Local/"
    lcd32_remote_dir = libraries_dir + "LCD32_Remote/"
    python_dir = "./"

    # Read in the XML file and check it for consistency:
    xml = XML()
    module_element = xml.read("./Vendors/sainsmart.com/LCD1602.xml", "Module")
    tags = XML_Check.tags_initialize()
    XML_Check.element_check(module_element, tags)
    module = Module(module_element, xml, style)

    #assert style.indent == 0
    #module.ino_slave_write(sketch_dir + "MB7_Slave.ino")

    assert style.indent == 0
    module.cpp_local_header_write(lcd32_local_dir + "LCD32_Local.h")

    assert style.indent == 0
    module.cpp_local_source_write(lcd32_local_dir + "LCD32_Local.cpp")

    assert style.indent == 0
    module.cpp_remote_header_write(lcd32_remote_dir + "LCD32_Remote.h")

    assert style.indent == 0
    module.cpp_remote_source_write(lcd32_remote_dir + "LCD32_Remote.cpp")

    assert style.indent == 0
    module.python_write("test.py")

    print style.indent
    assert style.indent == 0

if __name__ == "__main__":
    main()

