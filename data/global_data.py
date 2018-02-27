"""
Global variables for CARF
"""

#System
productions_root = 'D:/Productions/Projects'
users_root = 'D:/Productions/Users'
ctrls_shapes_file = 'D:/Dev/CARF/data/controls_shape.json'

#Sides for prefixes
left = 'L'
right = 'R'
center = 'M'
#Sides collection for loops
sides = [left, right]
positions_prefifx = [left, center, right]

#Validation lists
supported_rig_types = ['prop', 'layout', 'character','set'] #TODO Get this from directory?

#Colors for controllers
#Dictionary of sides with it's color assignation
sides_color = {
    left: 6,
    right: 13,
    center: 22
}
#Dictionary Made up of aribitray description-index pairs
colors_dict = {
    'blue': 6,
    'green': 14,
    'purple': 30,
    'red': 13,
    'yellow': 22,
    'light_blue' : 18,
    'light_green' : 26,
    'light_purple': 9, 
    'light_red': 20,
    'light_yellow': 21,
    'dark_blue' : 5, 
    'dark_green' : 7,
    'dark_purple': 31,
    'dark_red': 4,
    'dark_yellow': 25
}


#Project folder structure
# Dictionaries structure: Folder name(key) : another folder dictionary (value)
## use None as a value for a directory with no sub directories

#Creating assets sub dictionary based on supported assets.
assets_dict = {}
for asset in supported_rig_types:
    assets_dict[asset.capitalize()] = None

project_folders = {
    'Final':{
        'Assets':assets_dict,
        'Shots': None
    },
    'Checkins':{
        'Assets':assets_dict,
        'Shots': None
    }
}

#Asset folder structure
# asset_steps_folders = {
#     '':''
# }
asset_dev_folders = {
    'template': None,
    'weights': None,
    'wip': None,
    'scenes': None,
}