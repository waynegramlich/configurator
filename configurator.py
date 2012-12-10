#!/usr/bin/python
## @mainpage Configurator
#
# The configurator program provides a graphical user interface for
# configuring electronics projects made out of common modules selected
# from a database.
#
# Currently, it provides three subwindows:
#
# * A Selections sub-window that provides a database of modules.
#
# * A Project sub-window that shows all of the project modules and
#   how they interconnected.
#
# * A Module sub-window that shows information about the currently
#   selected module.

## @package configurator
#
# Graphical user inteface for configurator
#
# The configurator package implements the graphical user interface
# portion the Configurator using the Python Tkinter package.  The
# graphical user interface is kept separate from the main data
# structures.  Thus, someone who wanted to implement a user interface
# in wxPython would be able to do so without too much difficulty.

import glob                  # File wild card matching module
import os                # Operatin system utilities
import sys
print("sys.version_info=", sys.version_info)
if sys.version_info >= (3, 0):
    from tkinter import *        # Graphic User Interface took based ont Tcl/Tk
    import tkinter.filedialog
    ask_open_file_name = tkinter.filedialog.askopenfilename
else:
    from Tkinter import *
    import tkFileDialog        # Import a file dialog box
    ask_open_file_name = tkFileDialog.askopenfilename
from TreeWidget import TreeItem, TreeNode        # Tree widget for UI

from serial import *        # Serial communications package
from data_structures import *        # Data structures configurator
from maker_bus import *        # Serial to MakerBus routines

## @class Application
#
# Container of top level Application
#
# The *Application* class is the main application window.

class Application(Frame):


    ## The constructor
    #
    # The constructor initializes reads in the data and initializes
    # the application window

    def __init__(self, master = None):

        # Get the parent *Frame* initialized:
        Frame.__init__(self, master)

        # Read the data in:
        style = Style(self)
        self.maker_bus_base = None          # MakerBus base object
        self.project_file_name = None          # Project file name to read/write
        self.project_modified = False          # *True* => project tree modified
        self.project_root_item = None          # Root project *TreeItem* tree
        self.project_root_node = None          # Root project *Node* tree
        self.project_root_tree = None          # Root project *TreeNode* tree
        self.project_selected_item = None # Current selected project *TreeItem*
        self.register_or_function = None  # Current registor or function
        self.selected_module = None          # Currently selected *Module*
        self.selections_selected_item = None # Current selected sels. *TreeItem*
        self.selections_root_item = None  # Root selections *Node* tree
        self.selections_root_node = None  # Root selections *Node* tree
        self.selections_root_tree = None  # Root selections *TreeNode* tree
        self.style = style                  # Code generation style object

        self.tags = XML_Check.tags_initialize()
        self.xml = XML(style)

        # Create the root of the selections tree:
        selections_root_node = Selection("Selections", style)
        self.selections_root_node = selections_root_node

        modules_list = self.modules_read()
        modules_table = {}
        for module in modules_list:
            # Fill in the *modules_table*:      
            name = module.name
            vendor = module.vendor
            module_key = (vendor, name)
            modules_table[module_key] = module

            # Process the classifications:
            for classification in module.classifications:
                selection = selections_root_node
                levels = classification.levels
                for level in levels:
                    selection = selection.lookup_or_create(level)
                selection.module_append(module)
                selection.sort()
        self.modules_table = modules_table

        # Read in the project:
        project_file_name = "myproject.xml"
        self.project_file_name
        #project_root_node = self.project_read(project_file_name, modules_table)
        project_root_node = Project(None, modules_table, style)
        self.project_root_node = project_root_node

        #project_root_node.show(0)

        selections_root_item = \
          Shared_Tree_Item("Selections", selections_root_node, self, False)
        self.selections_root_item = selections_root_item
        project_root_item = \
          Shared_Tree_Item("Project", project_root_node, self, True)
        self.project_root_item = project_root_item

        # Force selections to the root of each tree:
        self.selections_selected_item = selections_root_item
        self.project_selected_item = project_root_item

        # Force the grid to fill the entire window frame.  Without this
        # window resizing does not work:

        self.grid(sticky = N + S + E + W)
        self.widgets_create()
        self.buttons_update()
        self.address_update()

        # Force the roots of both trees to be selected.
        self.entry_highlight(self.address_entry, True)
        self.selections_root_tree.select()
        self.project_root_tree.select()
        self.module_controls_update(None)

        # Open the serial port:
        device = "/dev/ttyUSB0"
        baud = 115200
        try:
            # Give 
            serial = Serial(device, baud)
        except SerialException:
            print("serial connection failed")
            serial = None

        # Did we open the serial connection?
        if serial == None:
            # No, remember that it did not open:
            maker_bus_base = None
        else:
            # Yes, create the *maker_bus_base* and *maker_bus_module*:
            maker_bus_base = Maker_Bus_Base(serial)

        # Remember whether or not we succeeded with the connection:
        self.maker_bus_base = maker_bus_base



    def address_entry_changed(self, string_variable):
        """ Application: This method is called when the address entry
            widget changes. """

        #print("address_entry_changed", string_variable, string_variable.get())
        self.address_update()

    def address_update(self):
        """ Application: Update the [Address Update] UI. """

        #print "=>Application.address_update(*):"

        address_entry = self.address_entry
        address_entry_text = address_entry.get()
        address_update_button = self.address_update_button

        node = self.project_selected_item.node
        if isinstance(node, Module_Use):
            module_use = node
            module = module_use.module_lookup(self.modules_table)
            assert isinstance(module, Module)
            if module_use.address != address_entry_text:
                address_re = re.compile(module.address_re)
                match = address_re.match(address_entry_text)
                if match:
                    #print "{0} matches {1}". \
                    #  format(address_entry_text, module.address_re)
                    self.button_highlight(address_update_button, True, "")
                else:
                    #print "{0} does not match {1}". \
                    #  format(address_entry_text, module.address_re)
                    self.button_highlight(address_update_button, False,
                      "Address is not valid (RE='{0}')". \
                      format(module.address_re))
            else:
                self.button_highlight(address_update_button, False,
                  "Adress matches one in project")
        elif isinstance(node, Project):
            self.button_highlight(address_update_button,
              False, "Project does not have an address")
        else:
            assert False

        #print "<=Application.address_update(*)"

    def address_update_button_click(self):
        """ Application: This method is invoke when the [Address Update]
            button is clicked.  It will change address of the currently
            selected *Module_Use* object. """

        #print "=>Application.address_update_button_click()"

        address_update_button = self.address_update_button
        why_not = self.address_update_button.why_not
        if why_not == None:
            node = self.project_selected_item.node
            if isinstance(node, Module_Use):
                module_use = node
                address_entry = self.address_entry
                address_entry_text = address_entry.get()
                if module_use.address != address_entry_text:
                    #print "modified"
                    module_use.address = address_entry_text
                    self.project_modified = True
            self.address_update()
            self.buttons_update()
        else:
            self.warn(why_not)

        #print "<=Application.address_update_button_click()"
            
    def append_button_click(self):
        """ Application: This method is invoke when the [Append} button
            is clicked.  It will insert a module on to the end of the
            currently selected project item/node. """

        why_not = self.append_button.why_not
        if why_not == None:
            # Get the module item and node:
            module_item = self.selections_selected_item
            module_node = module_item.node
            assert isinstance(module_node, Module)

            # Grab the module use item and node:
            module_use_item = self.project_selected_item
            module_use_node = module_use_item.node
            assert isinstance(module_use_node, Project) or \
              isinstance(module_use_node, Module_Use)

            # Get the tree roots:
            project_root_node = self.project_root_node
            project_root_tree = self.project_root_tree

            # Create the new *Module_Use* item and node:
            module_name = module_node.name
            vendor = module_node.vendor
            name_vendor_module = ( module_name, vendor, module_name )
            #print "name_vendor_module=", name_vendor_module
            new_module_use_node = \
              Module_Use(name_vendor_module, [ ], None, None, self.style)
            new_module_use_item = \
              Shared_Tree_Item(module_name, new_module_use_node, self, True)

            # Perform the append:
            module_use_tree = project_root_tree.node_find(module_use_item)
            assert module_use_tree != None
            module_use_tree.child_append(new_module_use_item)
            module_use_node.sub_node_append(new_module_use_node)

            # Update the project tree:
            project_root_tree.update()
            self.project_updated()

            # For debgging:
            #project_root_node.show(0)
            #print "============="
            #project_root_tree.show(0)
        else:
            self.warn(why_not)
            
    def button_create(self, frame, name, row, column, command):
        """ Application: Create and return a button widget inside
            of *frame* named *name* at (*row*, *column*).  *command*
            is the function excecuted when the button is clicked. """

        button = Button(frame, text = name, command = command)
        button.grid(row = row, column = column)
        return button

    def button_highlight(self, button, enable, why_not):
        #print "Application.button_highlight(*, {0}, {1})". \
        #  format("[{0}]".format(button.cget("text")), enable)
        background_color = "#FF8888"
        activebackground_color = background_color
        if enable:
            background_color = "#ffffff"        
            activebackground_color = "#88ff88"
            button.why_not = None
        else:
            button.why_not = why_not
        button.configure(background = \
          background_color, activebackground = activebackground_color)

    def buttons_update(self):
        """ Application: This method is invoked whenever it is time to
            update the button highlights. """

        #print "=>Application.buttons_update(*)"

        modules_table = self.modules_table

        # Now figure out if we have something that will work:
        selections_selected_item = self.selections_selected_item
        selections_selected_node = selections_selected_item.node
        project_selected_item = self.project_selected_item
        project_selected_node = project_selected_item.node
   
        # Deal with [Append] button:
        append_button = self.append_button
        if isinstance(selections_selected_node, Module):
            self.button_highlight(append_button,
              isinstance(project_selected_node, Project) or \
              isinstance(project_selected_node, Module_Use),
              "Must select project root, or another module")
        else:
            self.button_highlight(append_button, False,
              "No Module selected under Selections")

        # Deal with [Delete] button:
        self.button_highlight(self.delete_button,
          isinstance(project_selected_node, Module_Use),
          "No Module selected under Project")

        # Deal with [Prepend] button:
        prepend_button = self.prepend_button
        if isinstance(selections_selected_node, Module):
            self.button_highlight(prepend_button,
              isinstance(project_selected_node, Module_Use),
              "No Module selected under Project")
        else:
            self.button_highlight(prepend_button, False,
              "No Module selected under Selections")

        # Deal with [Save] button:
        self.button_highlight(self.save_button, self.project_modified,
          "Project unchanged, no need to save")

        # Deal with [Open] button:
        self.button_highlight(self.open_button, not self.project_modified,
          "Project is modified, need to save first")

        # Deal with [Generate] button:
        generate = ""
        if isinstance(project_selected_node, Module_Use):
            module_use = project_selected_node
            module = module_use.module_lookup(self.modules_table)
            assert isinstance(module, Module)
            generate = module.generate
        self.button_highlight(self.generate_button, generate != "",
          "Can not generate code for this module")

        #print "<=Application.buttons_update(*)"


    def call_button_click(self):
        """ Application: This method is called when it is time to
            call a function from the currently selected modue. """

        why_not = self.call_button.why_not
        if why_not == None:
            # Make sure we have a *Function*:
            function = self.register_or_function
            assert isinstance(function, Function)

            # Grab the associated *Module_Use*:
            project_selected_item = self.project_selected_item
            project_selected_node = project_selected_item.node
            assert isinstance(project_selected_node, Module_Use)
            module_use = project_selected_node

            # Positive function numbers are normal and negative are "special":
            function_number = function.number
            if function_number >= 0:
                # Normal function call:
        
                # The format of the entry field is:
                #
                #   "arg1 ... argnN ; result1 ... resultN"
                #
                # Where arg1 ... argN are function arguments
                # and everything after the semicolon is results
                # from the previous time.

                # Grab the call entry text and strip off from the semicolon on:
                call_entry = self.call_entry
                call_entry_text = self.call_entry.get()
                #print "call_entry_text (original)='{0}'". \
                #  format(call_entry_text)
                semicolon_index = call_entry_text.find(';')
                if semicolon_index >= 0:
                    call_entry_text = call_entry_text[0 : semicolon_index]
                call_entry_text = call_entry_text.strip(' ')
                #print "call_entry_text (just args)='{0}'". \
                #  format(call_entry_text)

                # Stuff the truncated value back into the call entry area:
                call_entry.delete(0, END)
                call_entry.insert(0, call_entry_text)

                # Split everyting into arguments:
                arguments = call_entry_text.split()
                #print "arguments=", arguments

                # Now convert everything to a number:
                number_arguments =[]
                for argument in arguments:
                    if argument.startswith("0x"):
                        # Deal with hexadecimal numbers starting with "0x...":
                        number = int(argument, 16)
                    elif len(argument) == 3 and \
                      argument[0] == "'" and argument[2] == "'":
                        # Deal with character literals '{char}':
                        number = ord(argument[1])
                    elif argument.isdigit():
                        # Assume it is a decimal integer:
                        number = int(argument)
                    else:
                        # We have an error:
                        self.warn("'{0}' converted to 0".format(argument))
                        number = 0
                    number_arguments.append(number)
                #print "number_arguments=", number_arguments

                number_arguments_length = len(number_arguments)
                parameters = function.parameters
                parameters_length = len(parameters)
                if parameters_length == number_arguments_length:
                    # We have something to send:

                    # Get the *Maker_Bus_Module* to use:
                    maker_bus_module = self.maker_bus_module_get(module_use)
                        
                    # First, start the command:
                    maker_bus_module.request_begin(module_use.offset + \
                      function_number)

                    # Second, iterate over all the parameters:
                    for index in range(parameters_length):
                        number = number_arguments[index]
                        parameter = parameters[index]
                        type = parameter.type
                        if type == "Byte":
                            maker_bus_module.request_byte_put(number)
                        elif type == "Character":
                            maker_bus_module.request_character_put(chr(number))
                        elif type == "Logical":
                            maker_bus_module.request_logical_put(number)
                        elif type == "UByte":
                            maker_bus_module.request_ubyte_put(number)
                        else:
                            assert False, "Finish dispatch table"

                    # Third, close of command request:
                    maker_bus_module.request_end()

                    # Forth: Grab the return values:
                    prefix = " ;"
                    results = function.results
                    for result in results:
                        type = result.type
                        if type == "Byte":
                            number = maker_bus_module.response_byte_get()
                        elif type == "Character":
                            number = maker_bus_module.response_character_get()
                        elif type == "Logical":
                            number = maker_bus_module.response_logical_get()
                        elif type == "UByte":
                            number = maker_bus_module.response_ubyte_get()
                        elif type == "UShort":
                            number = maker_bus_module.response_ushort_get()
                        else:
                            assert False, "Finish dispatch table"
                        call_entry_text += prefix + str(number)

                    # Fifth, put the final result back:
                    call_entry.delete(0, END)
                    call_entry.insert(0, call_entry_text)
                else:
                    # We have an error:
                    self.warn("Function needs %d% arguments, got %d% instead". \
                      format(parameters_length), number_arguments_length)
            else:
                # Special function:
                if function_number == -1:
                    # Reset
                    pass
                elif function_number == -2:
                    # Bus_Scan:

                    # Get the *Maker_Bus_Module* to use:
                    maker_bus_module = self.maker_bus_module_get(module_use)
                        
                    # Perform the bus scan:
                    maker_bus_module = module_use.maker_bus_module
                    maker_bus_base = maker_bus_module.maker_bus_base
                    ids = maker_bus_base.discovery_mode()
                    print("bus_scan=", ids)
                elif function_number == -3:
                    # Upload all
                    pass
                #print "function_number={0}".format(function_number)
        else:
            self.warn(why_not)

    def delete_button_click(self):
        """ Application: This method is called when the [Delete] button
            is clicked.  It deletes the currently selected module in
            the project tree. """

        why_not = self.delete_button.why_not
        if why_not == None:
            
            # Grab the module use item and node:
            module_use_item = self.project_selected_item
            module_use_node = module_use_item.node
            assert isinstance(module_use_node, Module_Use)

            # Get the root of the project:
            project_root_node = self.project_root_node
            project_root_tree = self.project_root_tree

            # Find the *parent_node* for *project_root_node*:
            module_use_parent_node, index = \
              module_use_node.parent_index_find(project_root_node)
            assert module_use_parent_node != None

            # Delete the appropriate item and node:
            module_use_item.delete(project_root_tree)
            module_use_parent_node.sub_node_delete(index)

            # We have just deleted the selected object.  Force the
            # project root to be the selected object:
            self.project_selected_item = self.project_root_item
            self.project_root_tree.select()

            # Update the project tree:
            project_root_tree.update()
            self.project_updated()

            # For debgging:
            #project_root_node.show(0)
            #print "============="
            #project_root_tree.show(0)
        else:
            self.warn(why_not)

    def entry_create(self,
      frame, row, column, column_span, text, string_variable, callback):
        """ Application: Create and return an entry widget inside
            of *frame* at grid position (*row*, *column*) that spans
            *column_span* grid columsn.  The initial value of the
            entry is *text*. """

        # Check argument types:
        assert isinstance(frame, Frame)
        assert isinstance(row, int)
        assert isinstance(column, int)
        assert isinstance(column_span, int)
        assert isinstance(text, str)
        assert string_variable == None or isinstance(string_variable, StringVar)

        # Create the *Entry* and specify the grid information:
        if string_variable == None:
            entry = Entry(frame, text = text)
        elif isinstance(string_variable, StringVar):
            string_variable = StringVar()
            string_variable.trace("w",
              lambda name, index, mode, var=string_variable: callback(var))
            entry = Entry(frame, text = text, textvariable = string_variable)
        else:        
            assert False
        entry.grid(row = row, column = column, columnspan = column_span,
          sticky = W)
        return entry

    def entry_update(self, string_variable, index):
        """ Application: This method is invoked each time """

        print("entry_update", string_variable,
          index, self.entry_names[index], string_variable.get())

    def entry_highlight(self, entry, enable):
        """ Application: This method will enable or disable *entry*
            depending upon *enable*. """

        # Check argument types:
        assert isinstance(entry, Entry)
        assert isinstance(enable, bool)

        if enable:
            entry.configure(background = "#ffffff", state = NORMAL)
        else:
            entry.delete(0, END)
            entry.configure(disabledbackground = "#FF8888", state = DISABLED)

    def generate_button_click(self):
        #print "[Generate] button click"

        why_not = self.open_button.why_not
        if why_not == None:
            # Pop up a file name chooser:
            #print "[Generate] button clicked"

            project_selected_item = self.project_selected_item
            project_selected_node = project_selected_item.node
            assert isinstance(project_selected_node, Module_Use)
            root_module_use = project_selected_node

            root_module = root_module_use.module_lookup(self.modules_table)
            assert isinstance(root_module, Module)

            generate = root_module.generate
            if generate == "Ino_Slave":
                name = project_selected_node.name
                sketch_generator = Sketch_Generator(name,
                  self.modules_table, self.style)

                root_module_use.sketch_generate(sketch_generator, 0)

                offsets_modified = \
                  sketch_generator.ino_slave_write(root_module_use)
                if offsets_modified:
                    self.project_modified = True
                    self.buttons_update()
            elif generate == "Python":
                project = self.project_root_node
                assert isinstance(project, Project)
                project.python_write(self.modules_table)
            else:
                assert False, \
                  "Unrecognized Generate attribute '{0}'".format(generate)

            #print "off_mod={0} pro_mod={1}". \
            #  format(offsets_modified, self.project_modified)
        else:
            self.warn(why_not)

    def get_button_click(self):
        """ Application: This method is called when it is time to
            get a register value from the currently selected module. """

        #print "[Get] button clicked"
        why_not = self.get_button.why_not
        if why_not == None:
            project_selected_item = self.project_selected_item
            project_selected_node = project_selected_item.node
            assert isinstance(project_selected_node, Module_Use)
            module_use = project_selected_node

            register = self.register_or_function
            assert isinstance(register, Register)
            type = register.type
            number = register.number

            # Get the *Maker_Bus_Module* to use:
            maker_bus_module = self.maker_bus_module_get(module_use)

            maker_bus_module.request_begin(module_use.offset + number)
            maker_bus_module.request_end()
            result = 0
            if type == "Logical":
                result = int(maker_bus_module.response_logical_get())
            elif type == "UByte":
                result = maker_bus_module.response_ubyte_get()
            elif type == "UShort":
                result = maker_bus_module.response_ushort_get()
            else:
                assert False
            get_entry = self.get_entry
            get_entry.delete(0, END)
            get_entry.insert(0, "{0}".format(result))
        else:
            self.warn(why_not)

    def label_create(self, frame, row, column, column_span, text):
        """ Application: This method will create a *Label* widget
            in *frame* at grid position (*row*, *column*) that
            spans *column_span* grid locations.  The initial label
            value is *text*. """

        # Check argument types:
        assert isinstance(frame, Frame)
        assert isinstance(row, int)
        assert isinstance(column, int)
        assert isinstance(column_span, int)
        assert isinstance(text, str)

        # Create the *Label* widget and specify the grid information:
        label = Label(frame, text = text, foreground = "red")
        label.grid(row = row,
          column = column, columnspan = column_span, sticky = W)
        return label

    def maker_bus_module_get(self, target_module_use):
        """ Application: This method will return the *Maker_Bus_Module* to
            use to access *module_use*. """

        #print "=>Application.maker_bus_module_get(*, '{0}')". \
        #  format(target_module_use.name)

        # Check arguemnt types:
        assert isinstance(target_module_use, Module_Use)
        
        # First see if we have cached the result:
        maker_bus_module = target_module_use.maker_bus_module
        if maker_bus_module == None:
            # Not cached, so go looking:

            # Get the project root node:
            project_root_node = self.project_root_node
            assert isinstance(project_root_node, Project)
            project = project_root_node

            # Recursively visit all of the mode_uses until we find the
            # one that matches:
            for sub_module_use in project.module_uses:
                maker_bus_module = \
                  self.maker_bus_module_get_helper(sub_module_use,
                  target_module_use, None, 1)

                # If a *Maker_Bus_Module* is returned:
                if isinstance(maker_bus_module, Maker_Bus_Module):
                    target_module_use.maker_bus_module = maker_bus_module
                    break

        #print "=>Application.maker_bus_module_get(*, '{0}') => {1}". \
        #  format(target_module_use.name, maker_bus_module != None)

        assert maker_bus_module != None

        return maker_bus_module

    def maker_bus_module_get_helper(self, current_module_use,
      target_module_use, maker_bus_module, indent):
        """ Application: Return the appropriate *Maker_Bus_Module* object
            to use with *target_module_use* starting from *current_module_use*.
            *maker_bus_module* passed recursively down until *target_module_use*
            is found. """

        
        #print "{0}=>App._get_helper(*, '{1}', '{2}', {3})". \
        #  format(" " * indent, current_module_use.name, target_module_use.name,
        #  maker_bus_module != None)

        result = None
        current_module = current_module_use.module_lookup(self.modules_table)

        #print "{0}address_type='{1}'". \
        #  format(" " * indent, current_module.address_type)

        if current_module.address_type == "MakerBus":
            # Recursive Maker_Bus nodes are not allowed, so we should
            # arrive at this point with *maker_bus_module* set to *None*:
            assert maker_bus_module == None

            # Is it cached:
            maker_bus_module = current_module_use.maker_bus_module
            if maker_bus_module == None:
                # Not cached; create it and cache it:
                maker_bus_module = Maker_Bus_Module(self.maker_bus_base,
                  int(current_module_use.address), 0)
                current_module_use.maker_bus_module = maker_bus_module

        # Have we found the desired *target_module_use*:
        if current_module_use == target_module_use:
            # Yes, cache *maker_bus_module* and return:
            target_module_use.maker_bus_module = maker_bus_module
            result = maker_bus_module
        else:
            # No, recursivly visit the nodes below:
            for sub_module_use in current_module_use.module_uses:
                result_maker_bus_module = \
                  self.maker_bus_module_get_helper(sub_module_use,
                  target_module_use, maker_bus_module, indent + 1)

                # If a *Maker_Bus_Module* is returned, we are done:
                if isinstance(result_maker_bus_module, Maker_Bus_Module):
                    result = result_maker_bus_module
                    break

        #print "{0}<=App._get_helper(*, '{1}', '{2}', {3}) => {4}". \
        #  format(" " * indent, current_module_use.name, target_module_use.name,
        #  maker_bus_module != None, result != None)

        return result

    def module_controls_update(self, register_or_function):
        """ Application: Update the highlighting of module controls. """

        #print "module_controls_update"

        # Check argument types:
        is_register = isinstance(register_or_function, Register)
        is_function = isinstance(register_or_function, Function)
        assert register_or_function == None or is_register or is_function

        # Remember what register/function was selected:
        self.register_or_function = register_or_function

        # Grab some values from *self*:
        address_update_button = self.address_update_button
        address_entry = self.address_entry
        call_button = self.call_button
        call_entry = self.call_entry
        get_button = self.get_button
        get_entry = self.get_entry
        set_button = self.get_button
        set_entry = self.get_entry
        button_highlight = self.button_highlight
        entry_highlight = self.entry_highlight

        # Generate different warning messages if no connection is open:
        if self.maker_bus_base == None:
            # No serial connection is open:
            button_highlight(get_button, False, "No serial connection")
            entry_highlight(get_entry, False)

            button_highlight(self.set_button, False, "No serial connection")
            entry_highlight(self.set_entry, False)

            button_highlight(self.call_button, False, "No serial connection")
            entry_highlight(self.call_entry, False)
        else:
            # Serial connection is open:
            button_highlight(get_button,
              is_register, "No register selected")
            entry_highlight(get_entry, is_register)

            button_highlight(self.set_button,
              is_register, "No register selected")
            entry_highlight(self.set_entry, is_register)

            button_highlight(self.call_button,
              is_function, "No function selected")
            entry_highlight(self.call_entry, is_function)

    def module_select(self, module):
        """ Application: Mark that *module* is selected. """

        #print "=>module_select()"

        assert isinstance(module, Module)

        # Clear the registers and functions:
        reg_and_func_list_box = self.reg_and_func_list_box
        reg_and_func_list_box.delete(0, END)

        self.selected_module = module
        registers = module.registers
        for register in registers:
            reg_and_func_list_box.insert(END,
              "{0}: {1}".format(register.name, register.type))
        functions = module.functions
        for function in functions:
            reg_and_func_list_box.insert(END,
              "{0:s}".format(function))

        # Disable the module controls until the user explicitly selects
        # a register or function:
        self.module_controls_update(None)

    def modules_read(self):
        tags = self.tags
        xml = self.xml
        style = self.style

        vendor_modules = []
        vendor_module_file_names = glob.glob("Vendors/*/*/*/*.xml")
        for vendor_module_file_name in vendor_module_file_names:
            style.file_name_set(vendor_module_file_name)
            vendor_module_element = xml.read(vendor_module_file_name, "Module")
            XML_Check.element_check(vendor_module_element, tags)
            vendor_module = \
              Module(vendor_module_element, vendor_module_file_name, style)
            vendor_modules.append(vendor_module)
        return vendor_modules

    def open_button_click(self):
        #print "[Open] button click"

        why_not = self.open_button.why_not
        if why_not == None:
            # Pop up a file name chooser:
            #project_file_name = \
            project_file_name = \
              ask_open_file_name(defaultextension = ".xml",
              initialfile = "myproject.xml", title = "Project file name",
              filetypes = [('XML files', '.xml'), ('All files', '.*')] )
            #print "project_file_name = '{0}'".format(project_file_name)
            self.project_file_name = project_file_name

            # Now read in the file:
            project_root_node = \
              self.project_read(project_file_name, self.modules_table)
            self.project_root_node = project_root_node

            # Create the new root *Shared_Tree_Item* object:
            project_root_item = \
              Shared_Tree_Item("Project", project_root_node, self, True)
            self.project_root_item = project_root_item

            # Release all the storage associated with the previous tree.
            self.project_root_tree.destroy()

            # Create a new tree and hook it up to the *project_canvas*:
            project_root_tree = \
              TreeNode(self.project_canvas, None, project_root_item)
            self.project_root_tree = project_root_tree

            # Force the root to be selected:
            self.project_selected_item = project_root_item

            # This breaks, why?
            #self.project_root_tree.select()

            # Now get the tree to be updated:
            project_root_tree.update()
            project_root_tree.expand()

    def prepend_button_click(self):
        why_not = self.prepend_button.why_not
        if why_not == None:
            #print "[Insert] button clicked"

            # Get the module item and node:
            module_item = self.selections_selected_item
            module_node = module_item.node
            assert isinstance(module_node, Module)

            # Grab the module use item and node:
            module_use_item = self.project_selected_item
            module_use_node = module_use_item.node
            assert isinstance(module_use_node, Module_Use)

            project_root_node = self.project_root_node
            project_root_tree = self.project_root_tree

            module_use_parent_node, index = \
              module_use_node.parent_index_find(project_root_node)
            assert module_use_parent_node != None

            # Create the new *Module_Use* item and node:
            module_name = module_node.name
            vendor = module_node.vendor
            name_vendor_module = ( module_name, vendor, module_name )
            #print "name_vendor_module=", name_vendor_module
            new_module_use_node = Module_Use(name_vendor_module,
              [ module_node ], None, None, self.style)
            new_module_use_item = \
              Shared_Tree_Item(module_name, new_module_use_node, self, True)

            module_use_item.prepend(new_module_use_item, project_root_tree)
            module_use_parent_node.sub_node_insert(index, module_node)

            # Update the project tree:
            project_root_tree.update()
            self.project_updated()

            # For debgging:
            #project_root_node.show(0)
            #project_root_tree.show(0)
        else:
            self.warn(why_not)

    def project_read(self, file_name, modules_table):
        assert isinstance(file_name, str)
        assert isinstance(modules_table, dict)

        tags = self.tags
        xml = self.xml
        style = self.style

        project_element = xml.read(file_name, "Project")
        XML_Check.element_check(project_element, tags)
        project = Project(project_element, modules_table, style)
        return project

    def project_updated(self):
        """ Application:  This method is invoked whenever the project
            tree is updated. """

        self.project_modified = True
        self.buttons_update()

    def register_or_function_selected(self, event):
        """ Application: This method is invoked whenver a register or
            function is selected in the registers/functions list box. """

        reg_and_func_list_box = application.reg_and_func_list_box
        selection = reg_and_func_list_box.curselection()
        #print "selection=", selection
        selection_index = int(selection[0])
        #print "selection_index=", selection_index

        module = self.selected_module
        if isinstance(module, Module):
            # Get the register, functions an associated length:
            registers = module.registers
            registers_length = len(registers)
            functions = module.functions
            functions_length = len(functions)

            # Dispatch on selection index
            if selection_index < registers_length:
                register = registers[selection_index]
                register_or_function = register
                self.module_controls_update(register)
            elif selection_index < registers_length + functions_length:
                function = functions[selection_index - registers_length]
                register_or_function = function
                self.module_controls_update(function)
            else:
                register_or_function = None
                self.module_controls_update(None)

            # Remember what was selected:
            self.register_or_function = register_or_function

    def set_button_click(self):
        """ Application: This method is called when it is time to
            set a register value from the currently selected modue. """

        why_not = self.set_button.why_not
        if why_not == None:
            project_selected_item = self.project_selected_item
            project_selected_node = project_selected_item.node
            assert isinstance(project_selected_node, Module_Use)
            module_use = project_selected_node

            register = self.register_or_function
            assert isinstance(register, Register)
            type = register.type
            number = register.number

            # Get the *Maker_Bus_Module* to use:
            maker_bus_module = self.maker_bus_module_get(module_use)

            set_entry_text = self.set_entry.get()
            if set_entry_text.isdigit():
                value = int(set_entry_text)
                maker_bus_module.request_begin(module_use.offset + number + 1)
                if type == "Logical":
                    result = maker_bus_module.request_logical_put(value)
                elif type == "UByte":
                    result = maker_bus_module.request_ubyte_put(value)
                elif type == "UShort":
                    result = maker_bus_module.request_ushort_put(value)
                else:
                    assert False
                maker_bus_module.request_end()
            else:
                self.warn("'{0}' is not a valid number".format(set_entry_text))
        else:
            self.warn(why_not)

    def tree_widget_create(self, parent_frame, root_item):
        frame = Frame(master = parent_frame)

        vertical_bar = Scrollbar(frame, orient = VERTICAL)
        horizontal_bar = Scrollbar(frame, orient = HORIZONTAL)
        canvas = Canvas(frame, bg = "white", \
          width = 300, height=300, scrollregion=(0, 0, 500, 500))

        canvas.config(width = 300, height = 300)        # Redundant?
        canvas.config(yscrollcommand = vertical_bar.set)
        canvas.config(xscrollcommand = horizontal_bar.set)
        horizontal_bar.config(command = canvas.xview)
        vertical_bar.config(command = canvas.yview)

        # Configure the frame weights:
        frame.rowconfigure(0, weight = 1)
        frame.columnconfigure(0, weight = 1)

        # Configure the ...
        frame.grid(row = 0, column = 0, sticky = N + S + E + W)
        canvas.grid(row = 0, column = 0, sticky = N + S + E + W)
        vertical_bar.grid(row = 0, column = 1, sticky = N + S)
        horizontal_bar.grid(row = 1, column = 0, sticky = E + W)

        # Create the tree widget:
        tree = TreeNode(canvas, None, root_item)
        tree.update()
        tree.expand()

        return frame, tree

    def scrollable_canvas_create(self, parent_frame):
        frame = Frame(master = parent_frame)

        vertical_bar = Scrollbar(frame, orient = VERTICAL)
        horizontal_bar = Scrollbar(frame, orient = HORIZONTAL)
        canvas = Canvas(frame, bg = "white", \
          width = 300, height= 300, scrollregion = (0, 0, 500, 500))

        canvas.config(width = 200, height = 300)        # Redundant?
        canvas.config(yscrollcommand = vertical_bar.set)
        canvas.config(xscrollcommand = horizontal_bar.set)
        horizontal_bar.config(command = canvas.xview)
        vertical_bar.config(command = canvas.yview)

        # Configure the frame weights:
        frame.rowconfigure(0, weight = 1)
        frame.columnconfigure(0, weight = 1)

        # Configure the ...
        frame.grid(row = 0, column = 0, sticky = N + S + E + W)
        canvas.grid(row = 0, column = 0, sticky = N + S + E + W)
        vertical_bar.grid(row = 0, column = 1, sticky = N + S)
        horizontal_bar.grid(row = 1, column = 0, sticky = E + W)

        return frame, canvas

    def scrollable_list_box_create(self, parent_frame):
        frame = Frame(master = parent_frame)

        vertical_bar = Scrollbar(frame, orient = VERTICAL)
        horizontal_bar = Scrollbar(frame, orient = HORIZONTAL)
        list_box = Listbox(frame, bg = "white", selectmode = SINGLE)

        list_box.config(width = 20, height = 30)
        list_box.config(yscrollcommand = vertical_bar.set)
        list_box.config(xscrollcommand = horizontal_bar.set)
        horizontal_bar.config(command = list_box.xview)
        vertical_bar.config(command = list_box.yview)

        list_box.bind("<<ListboxSelect>>", self.register_or_function_selected)

        # Configure the frame weights:
        frame.rowconfigure(0, weight = 1)
        frame.columnconfigure(0, weight = 1)

        # Configure the ...
        frame.grid(row = 0, column = 0, sticky = N + S + E + W)
        list_box.grid(row = 0, column = 0, sticky = N + S + E + W)
        vertical_bar.grid(row = 0, column = 1, sticky = N + S)
        horizontal_bar.grid(row = 1, column = 0, sticky = E + W)

        return frame, list_box

    def redo_button_click(self):
        print("[Redo] button clicked")

    def save_button_click(self):
        why_not = self.save_button.why_not
        if why_not == None:
            out_stream = open(self.project_file_name, "w")
            self.project_root_node.xml_write(0, out_stream)
            out_stream.close()
            self.project_modified = False
            self.buttons_update()
            self.address_update()
        else:
            self.warn(why_not)

    def undo_button_click(self):
        print("[Undo] button clicked")

    def warn(self, text):
        self.warn_label.config(text = text)
        #print "Warning: {0}".format(text)

    def widgets_create(self):
        """ Application: This method centralizes the creation of all the
            main window widgets. """

        # Create selections tree frame:
        selections_frame, selections_canvas = \
          self.scrollable_canvas_create(self)
        self.selections_frame = selections_frame
        self.selections_canvas = selections_canvas
        selections_root_tree = \
          TreeNode(selections_canvas, None, self.selections_root_item)
        self.selections_root_tree = selections_root_tree
        selections_root_tree.update()
        selections_root_tree.expand()

        # Create projects tree frame:
        project_frame, project_canvas = \
          self.scrollable_canvas_create(self)
        self.project_frame = project_frame
        self.project_canvas = project_canvas
        project_root_tree = \
          TreeNode(project_canvas, None, self.project_root_item)
        self.project_root_tree = project_root_tree
        project_root_tree.update()
        project_root_tree.expand()

        # Create the buttons frame:
        buttons_frame = Frame(self)
        self.buttons_frame = buttons_frame

        # Create each of the button in the buttons frame:
        self.append_button = \
          self.button_create(buttons_frame, "Append", 0, 0,
          self.append_button_click)
        self.prepend_button = \
          self.button_create(buttons_frame, "Prepend", 0, 1,
          self.prepend_button_click)
        self.delete_button = \
          self.button_create(buttons_frame, "Delete", 0, 2,
          self.delete_button_click)
        self.save_button = \
          self.button_create(buttons_frame, "Save", 0, 3,
          self.save_button_click)
        self.open_button = \
          self.button_create(buttons_frame, "Open", 0, 4,
          self.open_button_click)
        self.generate_button = \
          self.button_create(buttons_frame, "Generate", 0, 5,
          self.generate_button_click)
        self.warn_label = \
          self.label_create(buttons_frame, 1, 0, 5, "Warnings go here:")

        # Create the module_controls_frame:
        module_controls_frame = Frame(self)
        self.module_controls_frame = module_controls_frame

        # Create the module controls buttons and entries::
        self.address_update_button = \
          self.button_create(module_controls_frame, "Address Update", 0, 0,
          self.address_update_button_click)
        
        address_entry_variable = StringVar()
        self.address_entry = \
          self.entry_create(module_controls_frame, 0, 1, 1, "",
          address_entry_variable, self.address_entry_changed)
        self.get_button = \
          self.button_create(module_controls_frame, "Get", 1, 0,
          self.get_button_click)
        self.get_entry = \
          self.entry_create(module_controls_frame, 1, 1, 1, "", None, None)
        self.set_button = \
          self.button_create(module_controls_frame, "Set", 2, 0,
          self.set_button_click)
        self.set_entry = \
          self.entry_create(module_controls_frame, 2, 1, 1, "", None, None)
        self.call_button = \
          self.button_create(module_controls_frame, "Call", 3, 0,
          self.call_button_click)
        self.call_entry = \
          self.entry_create(module_controls_frame, 3, 1, 1, "", None, None)

        # Create module frame:
        module_list_box_frame, reg_and_func_list_box = \
          self.scrollable_list_box_create(self)
        self.module_list_box_frame = module_list_box_frame
        self.reg_and_func_list_box = reg_and_func_list_box

        # Start doing the grid weighting configuration:
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight = 1)
        top.columnconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 1)
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 1)

        # Now place all the widgets in grid for *self*:
        buttons_frame.grid(row = 0, column = 0, columnspan = 2,
          sticky = N + S + E + W)
        selections_frame.grid(row = 1, column = 0, sticky = N + S + E + W)
        project_frame.grid(row = 1, column = 1, sticky = N + S + E + W)
        module_list_box_frame.grid(row = 1, column = 2, sticky = N + S + E + W)
        module_controls_frame.grid(row = 0, column = 2, sticky = N + S + E + W)

## @class Shared_Tree_Item
#
# A specialization of tree widget TreeItem class.
#
# The tree widget package was originally taken from the tree widget
# package that came with the Python Idle programming environment.
# In retrospect, it would probably be better to start from scratch.
# There is a great deal of ugly code that surrounds the code that
# takes care of tree widget.
#
# The *correct* way is to modify *Node* so that it captures just
# the information needed to draw the tree.  This includes whether
# the node is expanded, expandable, its icon name, and text label.
# Upon a tree change, the entire tree should simply be redrawn.

class Shared_Tree_Item(TreeItem):

    def __init__(self, label, node, application, project_mode):
        """ Shared_Tree_Item: Initialize *self* to contain *label*,
            *node*, *application* and *project_mode*.  *label* is
            the text to be displayed by the tree widget.  *node*
            is the associated *Node* object.  *application* is the
            top level application which is used to keep track of
            the most recently selected *Shared_Tree_Item*.  If
            *project_mode* is *True*, *self* is in the project tree;
            otherwise it is in the selections tree. """

        # Catch argument type errors here:
        assert isinstance(label, str)
        assert isinstance(node, Node)
        assert isinstance(application, Application)
        assert isinstance(project_mode, bool)

        # Save the values away into *self*:
        self.application = application
        self.label = label
        self.node = node
        self.project_mode = project_mode
        
    def GetText(self):
        """ Shared_Tree_Item: Return the text label to be displayed
            for *self*. """

        return self.label

    def IsEditable(self):
        """ Shared_Tree_Item: Returns *True* if *self* is allowed to
            be edited. """

        # Only project mode items are editable:
        return self.project_mode

    def SetText(self, label):
        """ Shared_Tree_Item: Replace the label of *self* with *label*. """

        assert self.project_mode
        if self.label != label:
            self.label = label
            self.node.name = label
            self.application.project_updated()

    def GetIconName(self):
        """ Shared_Tree_Item: Return the name of the icon to display
            for *self* in the tree widget window.  """

        return "folder"

    def IsExpandable(self):
        """ Shared_Tree_Item: Return *True* if *self* can be expanded
            to show items nested below and *False* otherwise.  """

        # Return *True* if *sub_nodes* exists and is non-empty:
        sub_nodes = self.node.sub_nodes
        return sub_nodes != None and len(sub_nodes) != 0

    def GetSubList(self):
        """ Shared_Tree_Item: Return a list of *Shared_Tree_Item*
            objects that correspond to the items to be displayed on the
            widget under *self*.  """

        #print "Shared_Tree_Item.GetSubList({0}):mode:{1}". \
        #  format(self.label, self.project_mode)

        project_mode = self.project_mode
        tree_items = []
        node = self.node
        for sub_node in node.sub_nodes:
            tree_item = Shared_Tree_Item(sub_node.name,
              sub_node, self.application, project_mode)
            tree_items.append(tree_item)

        if not self.project_mode:
            tree_items.sort(key = lambda item: item.label)

        return tree_items

    def OnSelect(self):
        """ Shared_Tree_Item: This method is overriden to deal with
            when *self* is selected. """

        # Update the currently selected project item in *application*:
        application = self.application
        address_update_button = application.address_update_button
        if self.project_mode:
            application.project_selected_item = self

            node = self.node
            if isinstance(node, Module_Use):
                # Lookup the associated *Module* object:
                module_use = node

                # Update module address entry:
                address_entry = application.address_entry
                address_entry.delete(0, END)
                address_entry.insert(0, "{0}".format(module_use.address))

                # Properly highlight the [Address Update] button:
                application.address_update()

                # Look up the appropriate module:
                vendor = module_use.vendor
                modules_table = application.modules_table
                module_name = module_use.module_name
                module_key = (vendor, module_name)
                if module_key in modules_table:
                    #print "module_key=", module_key
                    module = modules_table[module_key]
                    assert isinstance(module, Module)
                    application.module_select(module)
        else:
            application.button_highlight(address_update_button, False,
              "Project does not have an address")
            application.selections_selected_item = self

        # Do all of the common code shared between the two tree widget
        application.buttons_update()

application = Application()
application.mainloop()
