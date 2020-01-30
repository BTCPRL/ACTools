"""
Config data for CARF
"""
import os

""" Paths """
drive = 'D:'
productions_root = '{}/Productions/Projects'.format(drive)
users_root = '{}/Productions/Users'.format(drive)
carf_root = '{}/Dev/CARF'.format(drive)
ctrls_shapes_file = '{}/data/controls_shape.json'.format(carf_root)

""" system """
_max_user_backups_ = 20


""" Builder """
# Sides for prefixes
left = 'L_'
right = 'R_'
center = 'M_'

# Sides collection for loops
sides = [left, right]
positions_prefifx = [left, center, right]

# Validation lists
rigtypes_path = '{}/rigs'.format(carf_root)
rig_dir_content = os.listdir(rigtypes_path)
rig_dir_content.remove('__init__.py')
supported_rig_types = [x.split('.')[0] for x in rig_dir_content]

# Rig groups
rig_base_groups = ['ctrls', 'geo', 'skeleton', 'setup']

""" Controls """
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
secondary_sides_color = {
    left: 15,
    right: 12,
    center: 21
}


""" Directories"""
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
