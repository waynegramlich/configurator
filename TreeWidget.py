## @package TreeWidget
#
# User interface tree widget
#
# This code was originally taken from the TreeWidget module developed
# for the Python Idle IDE.  It has been modified (hacked) to support
# the needs of the Configurator.

# XXX TO DO:
# - popup menu
# - support partial or total redisplay
# - key bindings (instead of quick-n-dirty bindings on Canvas):
#   - up/down arrow keys to move focus around
#   - ditto for page up/down, home/end
#   - left/right arrows to expand/collapse & move out/in
# - more doc strings
# - add icons for "file", "module", "class", "method"; better "python" icon
# - callback for selection???
# - multiple-item selection
# - tooltips
# - redo geometry without magic numbers
# - keep track of object ids to allow more careful cleaning
# - optimize tree redraw after expand of subnode

import os
import sys
if sys.version_info >= (3, 0):
    from tkinter import *
else:
    from Tkinter import *
import imp

from idlelib import ZoomHeight
from idlelib.configHandler import idleConf

ICONDIR = "Icons"

# Look for Icons subdirectory in the same directory as this module
try:
    _icondir = os.path.join(os.path.dirname(__file__), ICONDIR)
except NameError:
    _icondir = ICONDIR
if os.path.isdir(_icondir):
    ICONDIR = _icondir
elif not os.path.isdir(ICONDIR):
    #raise RuntimeError, "can't find icon directory (%r)" % (ICONDIR,)
    assert False

def listicons(icondir=ICONDIR):
    """Utility to display the available icons."""
    root = Tk()
    import glob
    list = glob.glob(os.path.join(icondir, "*.gif"))
    list.sort()
    images = []
    row = column = 0
    for file in list:
        name = os.path.splitext(os.path.basename(file))[0]
        image = PhotoImage(file=file, master=root)
        images.append(image)
        label = Label(root, image=image, bd=1, relief="raised")
        label.grid(row=row, column=column)
        label = Label(root, text=name)
        label.grid(row=row+1, column=column)
        column = column + 1
        if column >= 10:
            row = row+2
            column = 0
    root.images = images


## @class TreeNode
#
# One node of the TreeNode tree.
#
# TreeNode corresponds to nodes in the tree that have been visited
# by the tree node widget. 

class TreeNode:

    def __init__(self, canvas, parent, item):
        self.canvas = canvas
        self.parent = parent
        self.item = item
        self.state = 'collapsed'
        self.selected = False
        self.children = []
        self.x = self.y = None
        self.iconimages = {} # cache of PhotoImage instances for icons

    def show(self, level):
        """ TreeNode: Recursively print out *self* indented by *level*. """

        print("{0}TreeNode: item={1}  state={2} selected={3} expandable={4}". \
          format("  " * level, self.item.label, self.state, self.selected,
          self.item.expandable))
        children = self.children
        if children != None:
            for child in children:
                child.show(level + 1)

    def node_find(self, item):
        """ TreeNode: Recursively search for the *TreeNode* associated
            with *item*.  *None* is returned if not nothing is found. """

        #print "=>TreeNode.node_find({0}, {1})". \
        #  format(self.item.label, item.label)

        # Check argument types:
        assert isinstance(item, TreeItem)

        # Search through children:
        result = None
        if self.item == item:
            # Found *item* at this level:
            result = self
        else:
            # Search for *item* recursively:
            children = self.children
            for sub_node in children:
                find_match = sub_node.node_find(item)
                if find_match != None:
                    # We found *item* further down:
                    result = find_match
                    break
        
        #result_text = "None"
        #if result != None:
        #    result_text = result.item.label
        #print "<=TreeNode.node_find({0}, {1})=>{2}". \
        #  format(self.item.label, item.label, result_text)

        return result

    def parent_index_find(self, item):
        """ TreeNode: Recursively search for the parent *TreeNode*
            object of *item* and return both its associated *TreeNode*
            object and the index of its children list for *item*.
            (*None*, -1) is returned if nothing is found. """

        # Check argument types:
        assert isinstance(item, TreeItem)

        #print "=>TreeNode.parent_index_find match({0}, {1})". \
        #  format(self.item.label, item.label)

        # Search through children:
        result_node = None
        result_index = -1

        # Iterate across *children*:
        children = self.children
        for index in range(len(children)):
            child_node = children[index]
            if child_node.item == item:
                result_node = self
                result_index = index
                break

            # Recursively try children of *sub_node*:
            sub_node, sub_index = child_node.parent_index_find(item)
            if sub_node != None:
                result_node = sub_node
                result_index = sub_index
                break

        # Nope, nothing found:
        #result_text = "None"
        #if result_node != None:
        #    result_text = result_node.item.label
        #print "<=TreeNode.parent_index_find match({0}, {1}) => {2}, {3}". \
        #  format(self.item.label, item.label, result_text, result_index)

        return result_node, result_index

    def child_append(self, new_item):
        """ TreeNode: Append *new_item* to the children of *self*. """

        # Check argument types:
        assert isinstance(new_item, TreeItem)

        new_node = self.__class__(self.canvas, self, new_item)

        # Make sure that *children* exists:
        children = self.children
        if children == None:
            children = []
            self.children = children

        # Now perform the append:
        children.append(new_node)

        # Mark this node as expanded:
        self.state = 'expanded'

    def item_delete(self, index):
        """ TreeNode: Delete *TreeItem* from *index*'th slot of *self*. """

        # Check argument types:
        assert isinstance(index, int)

        #print "Tree_Node.item_delete({0}, {1}):expandable={2}". \
        #  format(self.item.label, index, self.item.expandable)

        children = self.children
        assert children != None
        assert index <= len(children)
        del children[index]

        if len(children) == 0:
            self.state = 'collapsed'
            self.item.expandable = False

    def item_insert(self, index, new_item):
        """ TreeNode: Insert *item* into the children of *self* at *index*. """

        # Check argument types:
        assert isinstance(index, int)
        assert isinstance(new_item, TreeItem)

        #print "TreeNode.item_insert({0}, {1}, {2})". \
        #  format(self.item.label, index, new_item.label)

        new_node = self.__class__(self.canvas, self, new_item)

        children = self.children
        if children == None:
            # We can only insert at 0:
            assert index == 0
            self.children = [ new_node ]
        else:
            assert index <= len(children)
            children.insert(index, new_node)

    def destroy(self):
        for c in self.children[:]:
            self.children.remove(c)
            c.destroy()
        self.parent = None

    def geticonimage(self, name):
        try:
            return self.iconimages[name]
        except KeyError:
            pass
        file, ext = os.path.splitext(name)
        ext = ext or ".gif"
        fullname = os.path.join(ICONDIR, file + ext)
        image = PhotoImage(master=self.canvas, file=fullname)
        self.iconimages[name] = image
        return image

    def select(self, event=None):
        if self.selected:
            return
        self.deselectall()
        self.selected = True
        self.canvas.delete(self.image_id)
        self.drawicon()
        self.drawtext()
        self.item.OnSelect()

    def deselect(self, event=None):
        if not self.selected:
            return
        self.selected = False
        self.canvas.delete(self.image_id)
        self.drawicon()
        self.drawtext()

    def deselectall(self):
        if self.parent:
            self.parent.deselectall()
        else:
            self.deselecttree()

    def deselecttree(self):
        if self.selected:
            self.deselect()
        for child in self.children:
            child.deselecttree()

    def flip(self, event=None):
        if self.state == 'expanded':
            self.collapse()
        else:
            self.expand()
        self.item.OnDoubleClick()
        return "break"

    def expand(self, event=None):
        if not self.item._IsExpandable():
            return
        if self.state != 'expanded':
            self.state = 'expanded'
            self.update()
            self.view()

    def collapse(self, event=None):
        if self.state != 'collapsed':
            self.state = 'collapsed'
            self.update()

    def view(self):
        top = self.y - 2
        bottom = self.lastvisiblechild().y + 17
        height = bottom - top
        visible_top = self.canvas.canvasy(0)
        visible_height = self.canvas.winfo_height()
        visible_bottom = self.canvas.canvasy(visible_height)
        if visible_top <= top and bottom <= visible_bottom:
            return
        x0, y0, x1, y1 = self.canvas._getints(self.canvas['scrollregion'])
        if top >= visible_top and height <= visible_height:
            fraction = top + height - visible_height
        else:
            fraction = top
        fraction = float(fraction) / y1
        self.canvas.yview_moveto(fraction)

    def lastvisiblechild(self):
        if self.children and self.state == 'expanded':
            return self.children[-1].lastvisiblechild()
        else:
            return self

    def update(self):
        if self.parent:
            self.parent.update()
        else:
            oldcursor = self.canvas['cursor']
            self.canvas['cursor'] = "watch"
            self.canvas.update()
            self.canvas.delete(ALL)     # XXX could be more subtle
            self.draw(7, 2)
            x0, y0, x1, y1 = self.canvas.bbox(ALL)
            self.canvas.configure(scrollregion=(0, 0, x1, y1))
            self.canvas['cursor'] = oldcursor

    def draw(self, x, y):
        # XXX This hard-codes too many geometry constants!
        self.x, self.y = x, y
        self.drawicon()
        self.drawtext()
        if self.state != 'expanded':
            return y+17
        # draw children
        if not self.children:
            sublist = self.item._GetSubList()
            if not sublist:
                # _IsExpandable() was mistaken; that's allowed
                return y+17
            for item in sublist:
                child = self.__class__(self.canvas, self, item)
                self.children.append(child)
        cx = x+20
        cy = y+17
        cylast = 0
        for child in self.children:
            cylast = cy
            self.canvas.create_line(x+9, cy+7, cx, cy+7, fill="gray50")
            cy = child.draw(cx, cy)
            if child.item._IsExpandable():
                if child.state == 'expanded':
                    iconname = "minusnode"
                    callback = child.collapse
                else:
                    iconname = "plusnode"
                    callback = child.expand
                image = self.geticonimage(iconname)
                id = self.canvas.create_image(x+9, cylast+7, image=image)
                # XXX This leaks bindings until canvas is deleted:
                self.canvas.tag_bind(id, "<1>", callback)
                self.canvas.tag_bind(id, "<Double-1>", lambda x: None)
        id = self.canvas.create_line(x+9, y+10, x+9, cylast+7,
            ##stipple="gray50",     # XXX Seems broken in Tk 8.0.x
            fill="gray50")
        self.canvas.tag_lower(id) # XXX .lower(id) before Python 1.5.2
        return cy

    def drawicon(self):
        if self.selected:
            imagename = (self.item.GetSelectedIconName() or
                         self.item.GetIconName() or
                         "openfolder")
        else:
            imagename = self.item.GetIconName() or "folder"
        image = self.geticonimage(imagename)
        id = self.canvas.create_image(self.x, self.y, anchor="nw", image=image)
        self.image_id = id
        self.canvas.tag_bind(id, "<1>", self.select)
        self.canvas.tag_bind(id, "<Double-1>", self.flip)

    def drawtext(self):
        textx = self.x+20-1
        texty = self.y-1
        labeltext = self.item.GetLabelText()
        if labeltext:
            id = self.canvas.create_text(textx, texty, anchor="nw",
                                         text=labeltext)
            self.canvas.tag_bind(id, "<1>", self.select)
            self.canvas.tag_bind(id, "<Double-1>", self.flip)
            x0, y0, x1, y1 = self.canvas.bbox(id)
            textx = max(x1, 200) + 10
        text = self.item.GetText() or "<no text>"
        try:
            self.entry
        except AttributeError:
            pass
        else:
            self.edit_finish()
        try:
            label = self.label
        except AttributeError:
            # padding carefully selected (on Windows) to match Entry widget:
            self.label = Label(self.canvas, text=text, bd=0, padx=2, pady=2)
        theme = idleConf.GetOption('main','Theme','name')
        if self.selected:
            self.label.configure(idleConf.GetHighlight(theme, 'hilite'))
        else:
            self.label.configure(idleConf.GetHighlight(theme, 'normal'))
        id = self.canvas.create_window(textx, texty,
                                       anchor="nw", window=self.label)
        self.label.bind("<1>", self.select_or_edit)
        self.label.bind("<Double-1>", self.flip)
        self.text_id = id

    def select_or_edit(self, event=None):
        if self.selected and self.item.IsEditable():
            self.edit(event)
        else:
            self.select(event)

    def edit(self, event=None):
        self.entry = Entry(self.label, bd=0, highlightthickness=1, width=0)
        self.entry.insert(0, self.label['text'])
        self.entry.selection_range(0, END)
        self.entry.pack(ipadx=5)
        self.entry.focus_set()
        self.entry.bind("<Return>", self.edit_finish)
        self.entry.bind("<Escape>", self.edit_cancel)

    def edit_finish(self, event=None):
        try:
            entry = self.entry
            del self.entry
        except AttributeError:
            return
        text = entry.get()
        entry.destroy()
        if text and text != self.item.GetText():
            self.item.SetText(text)
        text = self.item.GetText()
        self.label['text'] = text
        self.drawtext()
        self.canvas.focus_set()

    def edit_cancel(self, event=None):
        try:
            entry = self.entry
            del self.entry
        except AttributeError:
            return
        entry.destroy()
        self.drawtext()
        self.canvas.focus_set()


## @class TreeItem
#
# Abstract base class used to specialize the Tree widget.
#
# The *TreeItem* class is used to provide an abstract interface
# to the tree widget functionality.

class TreeItem:

    """Abstract class representing tree items.

    Methods should typically be overridden, otherwise a default action
    is used.

    """

    def __init__(self):
        """Constructor.  Do whatever you need to do."""

    def delete(self, root_tree_node):
        """ TreeNode: Delete *self* from the tree rooted at
            *root_tree_node*.  Do not ovrerride this mehod. """

        # Check argument types:
        assert isinstance(root_tree_node, TreeNode)

        parent_node, index = root_tree_node.parent_index_find(self)
        assert parent_node != None
        parent_node.item_delete(index)

    def prepend(self, new_item, root_tree_node):
        """ TreeNode: Prepend *new_item* to *self* using *root_tree_node*
            as the root of the entire tree.  Do not override this method. """

        # Check argument types:
        assert isinstance(new_item, TreeItem)
        assert isinstance(root_tree_node, TreeNode)

        parent_node, index = root_tree_node.parent_index_find(self)
        assert parent_node != None
        parent_node.item_insert(index, new_item)

    def append(self, new_item, root_tree_node):
        """ TreeNode: Append *new_item* to *self* using *root_tree_node*
            as the root of the entire tree.  Do no override this method. """

        # Check argument types:
        assert isinstance(new_item, TreeItem)
        assert isinstance(root_tree_node, TreeNode)

        parent_node, index = root_tree_node.parent_index_find(self)
        assert parent_node != None
        parent_node.item_insert(index + 1, new_item)

    def child_append(self, item, root_tree_node):
        """ TreeNode: Append *item* to the children of *self*.
            *root_tree_node* is needed to find the *TreeNode*
            associated with *self*. """

        # Check argument types:
        assert isinstance(item, TreeItem)
        assert isinstance(root_tree_node, TreeNode)

        # Find the *tree_node* associated with *self*.
        node = root_tree_node.node_find(self)
        assert node != None
        xxx
        node.child_append(item)

    def GetText(self):
        """Return text string to display."""

    def GetLabelText(self):
        """Return label text string to display in front of text (if any)."""

    expandable = None

    def _IsExpandable(self):
        """Do not override!  Called by TreeNode."""
        if self.expandable is None:
            self.expandable = self.IsExpandable()
        return self.expandable

    def IsExpandable(self):
        """Return whether there are subitems."""
        return 1

    def _GetSubList(self):
        """Do not override!  Called by TreeNode."""
        if not self.IsExpandable():
            return []
        sublist = self.GetSubList()
        if not sublist:
            self.expandable = 0
        return sublist

    def IsEditable(self):
        """Return whether the item's text may be edited."""

    def SetText(self, text):
        """Change the item's text (if it is editable)."""

    def GetIconName(self):
        """Return name of icon to be displayed normally."""

    def GetSelectedIconName(self):
        """Return name of icon to be displayed when selected."""

    def GetSubList(self):
        """Return list of items forming sublist."""

    def OnSelect(self):
        """Called when item is selected."""

    def OnDoubleClick(self):
        """Called on a double-click on the item."""


# Example application

## @class FileTreeItem
#
# Example file system browser.

class FileTreeItem(TreeItem):

    """Example TreeItem subclass -- browse the file system."""

    def __init__(self, path):
        self.path = path

    def GetText(self):
        return os.path.basename(self.path) or self.path

    def IsEditable(self):
        return os.path.basename(self.path) != ""

    def SetText(self, text):
        newpath = os.path.dirname(self.path)
        newpath = os.path.join(newpath, text)
        if os.path.dirname(newpath) != os.path.dirname(self.path):
            return
        try:
            os.rename(self.path, newpath)
            self.path = newpath
        except os.error:
            pass

    def GetIconName(self):
        if not self.IsExpandable():
            return "python" # XXX wish there was a "file" icon

    def IsExpandable(self):
        return os.path.isdir(self.path)

    def GetSubList(self):
        try:
            names = os.listdir(self.path)
        except os.error:
            return []
        names.sort(key = os.path.normcase)
        sublist = []
        for name in names:
            item = FileTreeItem(os.path.join(self.path, name))
            sublist.append(item)
        return sublist


# A canvas widget with scroll bars and some useful bindings

## @class ScrolledCanvas
#
# Example scrolled tree widget

class ScrolledCanvas:
    def __init__(self, master, **opts):
        if 'yscrollincrement' not in opts:
            opts['yscrollincrement'] = 17
        self.master = master
        self.frame = Frame(master)
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.canvas = Canvas(self.frame, **opts)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vbar = Scrollbar(self.frame, name="vbar")
        self.vbar.grid(row=0, column=1, sticky="nse")
        self.hbar = Scrollbar(self.frame, name="hbar", orient="horizontal")
        self.hbar.grid(row=1, column=0, sticky="ews")
        self.canvas['yscrollcommand'] = self.vbar.set
        self.vbar['command'] = self.canvas.yview
        self.canvas['xscrollcommand'] = self.hbar.set
        self.hbar['command'] = self.canvas.xview
        self.canvas.bind("<Key-Prior>", self.page_up)
        self.canvas.bind("<Key-Next>", self.page_down)
        self.canvas.bind("<Key-Up>", self.unit_up)
        self.canvas.bind("<Key-Down>", self.unit_down)
        #if isinstance(master, Toplevel) or isinstance(master, Tk):
        self.canvas.bind("<Alt-Key-2>", self.zoom_height)
        self.canvas.focus_set()
    def page_up(self, event):
        self.canvas.yview_scroll(-1, "page")
        return "break"
    def page_down(self, event):
        self.canvas.yview_scroll(1, "page")
        return "break"
    def unit_up(self, event):
        self.canvas.yview_scroll(-1, "unit")
        return "break"
    def unit_down(self, event):
        self.canvas.yview_scroll(1, "unit")
        return "break"
    def zoom_height(self, event):
        ZoomHeight.zoom_height(self.master)
        return "break"


# Testing functions

def test():
    from idlelib import PyShell
    root = Toplevel(PyShell.root)
    root.configure(bd=0, bg="yellow")
    root.focus_set()
    sc = ScrolledCanvas(root, bg="white", highlightthickness=0, takefocus=1)
    sc.frame.pack(expand=1, fill="both")
    item = FileTreeItem("C:/windows/desktop")
    node = TreeNode(sc.canvas, None, item)
    node.expand()

def test2():
    # test w/o scrolling canvas
    root = Tk()
    root.configure(bd=0)
    canvas = Canvas(root, bg="white", highlightthickness=0)
    canvas.pack(expand=1, fill="both")
    item = FileTreeItem(os.curdir)
    node = TreeNode(canvas, None, item)
    node.update()
    canvas.focus_set()

if __name__ == '__main__':
    test()
