import pymel.core as pm 
import maya.cmds as cmds

from CARF.data import global_data as g_data
from CARF.maya_core import transforms as trans

class Joint(trans.Transform):
    """docstring for Joint."""
    def __init__(self, name, **Kwargs):

        #Args validation
        suffix = name.split('_')[-1]
        if suffix != 'JNT':
            name = '{}_JNT'.format(name)

        super(Joint, self).__init__(node_type = 'joint',name = name,**Kwargs)

        pm.makeIdentity(self.pm_node, apply = 1)
        pm.joint(self.pm_node, edit=True, orientJoint='xyz', 
            secondaryAxisOrient='xup', children=False, zeroScaleOrient=True)

        