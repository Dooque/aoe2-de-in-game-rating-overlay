#!/usr/bin/env python
'''A Demo of method to modify right-click menu based on tree item selection.
A right-Click on the Tree causes the item under it to be selected.  
The Right-Click Menu is then modified based on that selection.
Uses sub-classed sg.Tree and an extra class MenuChoices.
'''

#%% imports etc.
from typing import List, NamedTuple
import PySimpleGUI as sg


#%% Some helper classes because I am lazy
class TreeGroup(NamedTuple):
    '''Values that define a Tree Node.
    Note: I recommend using a NamedTuple for TreData values.  This makes it
        easy to access and use these values from within your GUI.
    '''
    name: str
    parent: str = ''
    text: str = None
    number1: float = 0.0
    number2: float = 0.0
    menu_key: str = None


class ColumnSettings(NamedTuple):
    '''Settings for individual columns in a tree.
    Some of the settings that can be applied to an individual column.
    Positional Arguments:
        name {str} -- The column text.
        width {int} -- The default width of the column. Default is 30.
        show {bool} -- Display the column. Default is True.
    '''
    name : str
    width : int = 30
    show : bool = True


class ColumConfig(list):
    '''Column settings for a list of columns.
    A helper class that makes the defining and implementing of tree columns
    easier and clearer.
    '''
    def __init__(self, settings_list: List[ColumnSettings]):
        '''Generate a list of column settings.
        Arguments:
            settings_list {List[ColumnSettings]} -- A list of column settings
                for each column.  The list order should match the order of the
                items in the values passed to TreeData.  The list may contain
                one column with the name 'col0' - representing the key column. 
                The settings for this column are removed from the name_list and
                width_list lists and separately assigned to column0 keyword
                arguments given by column_kwargs().
        '''
        super().__init__()
        for settings in settings_list:
            self.add(settings)

    def add(self, settings: ColumnSettings):
        '''Add settings for a column.
        '''
        # Reapply ColumnSettings conversion to allow for plain tuples
        # being passed.
        self.append(ColumnSettings(*settings))

    def name_list(self)->List[str]:
        '''Return a list of column names.
        '''
        return [col.name for col in self if 'col0' not in col.name]

    def width_list(self)->List[str]:
        '''Return a list of column widths.
        '''
        return [col.width for col in self if 'col0' not in col.name]

    def col0_width(self)->List[str]:
        '''Return the 0 column width.
        '''
        col0_settings = [col for col in self if 'col0' in col.name]
        if col0_settings:
            width = col0_settings[0].width
        else:
            width = None
        return width

    def show_list(self)->List[str]:
        '''Return a column display map.
        '''
        return [col.show for col in self if 'col0' not in col.name]

    def column_kwargs(self, **kwargs):
        '''returns a keyword dict of column settings for a tree.
        Creates the: headings, visible_column_map, col_widths and col0_width
        options.
        Appends any additional options provided.
        Arguments: 
            Any valid Column keyword arguments.
        '''
        kwarg_dict = dict(
            headings=self.name_list(),
            visible_column_map=self.show_list(),
            col_widths=self.width_list())
        width0 = self.col0_width()
        if width0:
            kwarg_dict.update({'col0_width': width0})
        kwarg_dict.update(kwargs)
        return kwarg_dict


def build_tree(tree_pattern: TreeGroup)->sg.TreeData:
    '''Assemble the test tree data
    '''
    treedata = sg.TreeData()
    for item in tree_pattern:
        if item.parent not in treedata.tree_dict:
            treedata.Insert('', item.parent, item.parent, values=item)
        treedata.Insert(item.parent, item.name, item.name, values=item)
    return treedata



#%% The Key Ingredient
#       This is where all the interesting stuff happens.
class MenuDict(dict):
    '''Modifies a basic dictionary to defines a Default Menu if no matching
    selection is found.  Otherwise, just an ordinary dictionary.
    '''
    def __init__(self, *args, default=None, **kwargs):
        '''Accept a default definition at initialization.
        Arguments:
            default {List[Any}} -- The default menu. If not supplied use:
                ['Default', ['Default Menu', 'One', '&Two', '&More']
        '''
        super().__init__(self, *args, **kwargs)
        if default is None:
            default = ['Default', ['Default Menu', 'One', '&Two', '&More']]
        self.default_menu = default

    def __missing__(self, key):
        '''Return self.default_menu if key is not in the dictionary.
        '''
        return self.default_menu


class MenuChoices():
    '''Add options to modify the right-click menu.
    '''
    def __init__(self, *args, menu_dict: MenuDict = None, **kwargs):
        '''Add a menu selection dictionary to the element.
        Arguments:
            menu_choices {MenuDict, None} -- A dictionary with the values as
                Menu definition lists and the key, the reference to the menu. 
        '''
        # super().__init__(*args, **kwargs) allows this class to be embedded
        #    in an inheritance chain. In the current situation it serves no
        #    function.
        super().__init__(*args, **kwargs) 
        if menu_dict is None:
            self.menu_choices = MenuDict(default=self.RightClickMenu)
        else:
            self.menu_choices = menu_dict
        # Currently forces the default to be the menu definition passed to
        #     self.RightClickMenu.  Comment it out to allow a default defined
        #     in menu_dict
        self.menu_choices.default_menu = self.RightClickMenu

    def clear_menu(self):
        '''Remove all menu items from a right-click menu.
        '''
        rt_menu = self.TKRightClickMenu
        # This call is directly to the Tkinter menu widget.
        rt_menu.delete(1,'end')

    def update_menu(self):
        '''Replace the current right-click menu with an updated menu contained
        in self.RightClickMenu.
        '''
        self.clear_menu()
        rt_menu = self.TKRightClickMenu
        menu =  self.RightClickMenu
        # This calls the sg menu creation method, normally called when the
        #     element is created.
        sg.AddMenuItem(rt_menu, menu[1], self)                    

    def select_menu(self, menu_key: str):
        '''Change the right-click menu based on the menu definition referenced
        by menu_key.  
        Arguments:
            menu_key {str} -- The dictionary key for the desired menu. If
                menu_key does not match any item in the dictionary, the
                original menu definition given to self.RightClickMenu will be
                used. 
        '''        
        self.RightClickMenu = self.menu_choices[menu_key]
        self.update_menu()


class TreeRtClick(MenuChoices, sg.Tree):
    '''A variation of the sg.Tree class that replaces the right-click callback
    function with one that first selects the tree item at the location of the
    right-click and then modified the right-click menu accordingly.
    Arguments:
        menu_dict {MenuDict, None} -- A dictionary with Menu definition lists
            as the values and a string key as the reference to the menu. 
        '''
    def get_key(self)->str:
        '''Get the appropriate menu key for the selected tree item.
        Returns:
            str -- The menu key for selecting the appropriate right-click menu
        '''
        selected_key = self.SelectedRows[0]
        ref = self.TreeData.tree_dict[selected_key].values
        if ref:
            return ref.menu_key
        # If ref is empty, then the right-click was not over an item.
        return None

    def _RightClickMenuCallback(self, event):
        '''
        Replace the parent class' right-click callback function with one that
        first selects the tree item at the location of the right-click.
        Arguments:
            event {tk.Event} -- A TK event item related to the right-click.
        '''
        # Get the Tkinter Tree widget
        tree = self.Widget  
        # These two calls are directly to the Tkinter Treeview widget.
        item_to_select = tree.identify_row(event.y) # Identify the tree item
        tree.selection_set(item_to_select)  # Set that item as selected.
        # Update the selected rows
        self.SelectedRows = [self.IdToKey[item_to_select]]
        # Set the corresponding menu.
        menu_key = self.get_key()
        if menu_key is None:
            # If menu_key is None, then the right-click was not over an item.
            # Ignore this rich-click
            return None 
        # Set the appropriate right-click menu
        self.select_menu(menu_key)  
        # Continue with normal right-click menu function.
        super()._RightClickMenuCallback(event) 


#%% Test tree and right-click menu items

# The default Menu
common_menu = ['AnyThing1','AnyThing2',"Any Those"]    
# The possible Right-Click Menus
right_menu_collection = MenuDict(
    M1 = ["",["First That", common_menu, "First This","First There"]],
    M2 = ["",["Second That", "Second This", common_menu,"Second There"]],
    M3 = ["",["Third That", "Third This","Third There", common_menu]],
    default = ["",["Nothing", common_menu]]
    )
# Give names for each column from values, their default width and whether to
#   display the column
columns = ColumConfig([
    ColumnSettings('col0', 10),
    ColumnSettings('Name', 10, False),
    ColumnSettings('Parent',10, False),
    ColumnSettings('Text', 15, True),
    ColumnSettings(' # 1', 3, True),
    ColumnSettings(' # 2', 3, True),
    ColumnSettings('Menu Key', 6, True)
    ])       
# Assemble all options for the Tree
tree_config = columns.column_kwargs(auto_size_columns=False, num_rows=10,
                                    show_expanded=True, enable_events=True)
# Define all of the data to be entered into the Tree
tree_pattern = [
    TreeGroup('aaa', 'First', 'First aaa', 8, 5, 'M1'),
    TreeGroup('bbb', 'First', 'First bbb', 9, 8, 'M1'),
    TreeGroup('ccc', 'First', 'First ccc', 7, 5, 'M1'),
    TreeGroup('Second', 'First', 'First Second', 5, 3, 'M1'),
    TreeGroup('111', 'Second', 'Second 111', 9, 4, 'M2'),
    TreeGroup('222', 'Second', 'Second 222', 3, 5, 'M2'),
    TreeGroup('333', 'Second', 'Second 333', 6, 1, 'M2'),
    TreeGroup('Third', 'First', 'First Third', 7, 2, 'M3'),
    TreeGroup('444', 'Third', 'Third 444', 5, 10, 'M3'),
    TreeGroup('zzz', 'Third', 'Third zzz', 5, 6, 'M3'),
    TreeGroup('yyy', 'Second', 'Second yyy', 5, 2, 'M2'),
    TreeGroup('xxx', 'Third', 'Third xxx', 8, 6, 'M3'),
    TreeGroup('xyz', 'Anything', 'Anything xyz', 9, 8, )
    ]


#%% Build the Test Window
treedata = build_tree(tree_pattern)
layout = [
    [sg.Text('Modifiable Right-Click Menu Demo',
             font=('Cambria',16,'bold'),
             justification='center')
    ],
    [TreeRtClick(data=treedata,
                 key='TestTree',
                 right_click_menu=right_menu_collection.default_menu,
                 menu_dict=right_menu_collection,
                 **tree_config)
    ],
    [sg.Button('Done')]
    ]
window = sg.Window('Tree Element Test', layout, finalize=True,)
window['TestTree'].expand(expand_x=True, expand_y=True)


#%% Run the Demo
while True:     # Event Loop
    event, values = window.read()
    if event in (None, 'Done'):
        break
    if values["TestTree"]:
        print(f'Event:\t{event}\n\t\tSelected Item = {values["TestTree"][0]}')
window.close()
