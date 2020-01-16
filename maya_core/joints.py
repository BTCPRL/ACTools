import maya.cmds as cmds

from CARF.data import global_data as g_data
from CARF.maya_core import transforms as trans


class Joint(trans.Transform):
    """docstring for Joint."""

    def __init__(self, name, **Kwargs):

        # Args validation
        suffix = name.split('_')[-1]
        if suffix != 'JNT':
            name = '{}_JNT'.format(name)

        super(Joint, self).__init__(node_type='joint', name=name, **Kwargs)

        # Orienting the joint
        cmds.makeIdentity(self.name, apply=1)
        cmds.joint(self.name, edit=True, orientJoint='xyz',
                   secondaryAxisOrient='xup', children=False,
                   zeroScaleOrient=True)

        # Labeling the joint
        label_joint(self.name)


def label_joint(jnt_name):
    """ Sets the label value for the joint
    It bases the side and the label on self.name. Type is always "other"
    """
    if jnt_name.split('_')[0] not in g_data.positions_prefifx:
        raise ValueError('Joint labeling only works with a valid side prefix')

    jnt_label = jnt_name[2:]
    label_side_options = {
        'L': 1,
        'M': 0,
        'R': 2,
    }
    label_side = label_side_options[jnt_name[0]]
    cmds.setAttr('{}.type'.format(jnt_name), 18)  # Custom label
    cmds.setAttr('{}.otherType'.format(jnt_name),
                 jnt_label, type='string')
    cmds.setAttr('{}.side'.format(jnt_name), label_side)
