# Sys imports
import json

# Maya imports
import maya.cmds as cmds
import pymel.core as pm
# Global data import
from CARF.data import global_data as g_data
# Modules improt
from CARF.maya_core import transforms as trans

reload(trans)


class Control(trans.Transform):
    """Control class deals with a collection of maya nodes that represent
        an animation controller. Usually includes one or multiple groups and 
        a nurbs curve
    """

    def __init__(self, name, shape, color=None, size=1,
                 ctr_type='main', tweak_ctrls=0, **kwargs):
        """ Control Creator
        :Args:
            name (str): Name of the controller, if 'CTR' suffix is not provided
                        it will be added
            shape (str): Shape for the nurbs curve of the controller
            color (str or int): Color of the nurbs curve (check set_color())
            size (int): Size of the shape
            ctr_type(str): Will determine a shift in the controller color
            tweak_ctrls(int): Number of sub controls to add under the main one
            **kwargs: Check the Transform class for more options
        """

        # Default attributes
        self.shapes = []
        self.size = size
        self.ctr_type = ctr_type
        self.last_ctr = self

        ctr_name = name
        if not name.split('_')[-1] == '_CTR':
            ctr_name = '%s_CTR' % ctr_name

        super(Control, self).__init__(
            name=ctr_name,
            node_type='control',
            **kwargs
        )

        # Template modifiers
        if ctr_type == 'template':
            shape = 'cube'

        # Create shape
        self.create_ctr_shape(shape)

        # Add color to shape
        if color:
            ctr_color = color
        elif self.ctr_type in ['secondary', 'tweak', 'template']:
            ctr_color = g_data.template_sides_color[side]
        else:
            ctr_color = g_data.sides_color[side]

        self.set_color(color=ctr_color)

        # Adding tweak ctrls
        if ctr_type != 'template':
            tweak_name = '{}_tweak'.format(name)
            for i in range(tweak_ctrls):
                if i:
                    tweak_name = '{}_tweak_{}'.format(name, i)
                tweak_ctrl = Control(
                    name=tweak_name,
                    side=side,
                    shape=shape,
                    size=1 - ((i + 1) / 10.00),
                    color=color,
                    add_space=False,
                    add_zero=False,
                    ctr_type='tweak',
                    parent=self.last_ctr,
                    match_object=self
                )
                self.last_ctr = tweak_ctrl

    def create_ctr_shape(self, shape):
        """ Creates curve shape and parents it under ctr transform
        """
        # Loads shapes dictionary
        shape_file_read = open(g_data.ctrls_shapes_file, 'r')
        shapes_dictionary = json.load(shape_file_read)

        # Args validation
        if not shape in shapes_dictionary.keys():
            raise Exception('%s is not a registered shape')

        # Extracts data
        shapes_data = shapes_dictionary[shape]
        for curve_data in shapes_data.keys():
            curve_degree = shapes_data[curve_data]['degree']
            curve_form = shapes_data[curve_data]['form']

            # Points are multiplied by size
            point_data = shapes_data[curve_data]['points']
            curve_points = []
            for each_point in point_data:
                sized_p = [p * self.size for p in each_point]
                curve_points.append(sized_p)
            # curve_points = [p*self.size for p in point_data]

            # Create curve in maya
            temp_curve = cmds.curve(name=self.full_name, degree=curve_degree,
                                    point=curve_points)
            if curve_form == 2:  # 2 is closed
                cmds.closeCurve(temp_curve, preserveShape=False,
                                replaceOriginal=True)

            curve_shape = temp_curve.getShape()
            # Parent curve shape under control and delete temp transform
            cmds.parent(curve_shape, self.node, r=1, s=1)
            cmds.delete(temp_curve)

            # Store shape in object attribute
            self.shapes.append(curve_shape)

    def set_color(self, color):
        """Description
        Args:
            color (str) : if passed as a string, it can be one of the following
                    options: 'blue', 'red', 'yellow', 'green', 'pink'.
                    Prefixes available for the options: 'light_' and 'dark_'
                    Examples: 'dark_red', 'light_green', 'pink'
            color (int) : if passed as an int, it represents the index value of
                    the Color attribute in the Drawing override tab for Maya
        """

        if type(color) is int:
            color_index = color
        elif type(color) is str:
            color_index = g_data.colors_dict[color]
        else:
            raise Exception('Color should be an integer or a string')

        for shape in self.shapes:
            cmds.setAttr('%s.overrideEnabled' % shape, 1)
            cmds.setAttr('%s.overrideColor' % shape, color_index)


def get_curve_data(shape):
    """Gets shape's degree and point information
    Returns the name of the curve, degree and point positio (In that order)
    """

    curve_degree = cmds.getAttr('%s.degree' % shape)
    curve_spans = cmds.getAttr('%s.spans' % shape)
    curve_form = cmds.getAttr('%s.form' % shape)

    points = curve_degree + curve_spans

    if curve_form == 2:
        points = curve_spans
    curve_points = []
    for i in range(points):
        curve_points.append(cmds.pointPosition('%s.cv[%i]' % (shape, i), l=1))

    curve_data = [curve_degree, curve_form, curve_points]

    return curve_data


def set_ctrl_shape(ctr_name, shape_info):
    """ Moves the shape's CVs into the given world position
    :args:
    shape_info (dict): 
            Dictionary with a world position for each of the ctrl's cvs
    """
        if not cmds.objExists(ctr_name):
            print '%s was not found, shapes not imported.' % ctr_name
            return False

        for shape in shape_info:
            points = shape_info[shape]['points']
            for i, p in enumerate(points):
                cmds.xform('%s.cv[%i]' % (shape, i), os=1, ws=0, t=p)


def export_ctrl_shape(ctr_name):
    """For a given ctrl, returns it's shapes degree, from and points
    """
    entries = {}

    data_dict = {
        ctr_name: entries
    }

    for x, shape in enumerate(cmds.listRelatives(ctr_name, shapes=1)):
        shape_data = get_curve_data(shape)
        entries[shape] = {
            'degree': shape_data[0],
            'form': shape_data[1],
            'points': shape_data[2]
        }
    return data_dict


def add_to_controls_shape(ctr_name):
    """ Adds control to control shape file
    """
    # get data
    ctr_dictionary = export_ctrl_shape(ctr_name)

    # Open Json file and Merge dictionaries
    shape_file_read = open(g_data.ctrls_shapes_file, 'r')
    current_shapes = json.load(shape_file_read)
    current_shapes.update(ctr_dictionary)

    j_data = current_shapes.copy()
    shape_file_read.close()

    # Save new json file
    shape_file_write = open(g_data.ctrls_shapes_file, 'w')

    json.dump(
        j_data,
        shape_file_write,
        indent=4,
        sort_keys=True
    )

    shape_file_write.close()


def create_all_ctrls():
    """ Creates all available ctrl shapes in the current scene
    """
    shape_file_read = open(g_data.ctrls_shapes_file, 'r')
    current_shapes = json.load(shape_file_read)
    x = 0
    for shape in current_shapes.keys():
        temp_ctr = Control(
            name=shape,
            side='M',
            shape=shape,
            position=[x, 0, 0, 0, 0, 0, ]
        )
        x = x + 3
