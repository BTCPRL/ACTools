"""
Global variables for CARF
"""

# System
productions_root = 'D:/Productions/Projects'
users_root = 'D:/Productions/Users'
ctrls_shapes_file = 'D:/Dev/CARF/data/controls_shape.json'

# Builder
# TODO:  better define stages, and when will these be used
builder_stages = ['init', 'template', 'build', 'finalize']

# Sides for prefixes
left = 'L'
right = 'R'
center = 'M'

# Sides collection for loops
sides = [left, right]
positions_prefifx = [left, center, right]

# Validation lists
# TODO Get this from directory?
supported_rig_types = ['prop', 'layout', 'character', 'set']

# Rig groups
rig_base_groups = ['ctrls', 'geo', 'skeleton', 'setup']

# Controls
# Colors for controllers
# Dictionary Made up of aribitray description-index pairs
colors_dict = {
    'blue': 6,
    'green': 14,
    'purple': 30,
    'red': 13,
    'yellow': 17,
    'light_blue': 18,
    'light_green': 26,
    'light_purple': 9,
    'light_red': 20,
    'light_yellow': 22,
    'dark_blue': 5,
    'dark_green': 7,
    'dark_purple': 31,
    'dark_red': 4,
    'dark_yellow': 25
}
# Dictionary of sides with it's color assignation
sides_color = {
    left: 6,
    right: 13,
    center: 22
}
template_sides_color = {
    left: 15,
    right: 12,
    center: 21
}


# Directories
# Project folder structure
# Dictionaries structure: Folder name(key) : another folder dictionary (value)
# use None as a value for a directory with no sub directories

# Creating assets sub dictionary based on supported assets.
assets_dict = {}
for asset in supported_rig_types:
    assets_dict[asset.capitalize()] = None

project_folders = {
    'Final': {
        'Assets': assets_dict,
        'Shots': None
    },
    'Checkins': {
        'Assets': assets_dict,
        'Shots': None
    }
}

# Asset folder structure
asset_dev_folders = {
    'template': None,
    'weights': None,
    'wip': None,
    'scenes': None,
    'shapes': None
}
