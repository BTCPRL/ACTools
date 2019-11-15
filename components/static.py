from CARF.components import component
from CARF.maya_core import controls
from CARF.maya_core import transforms as trans

class Static(component.Component):
    """Static component
    Creates only one main control. It can optionally have one joint 

    Component args:
        scale_constrained (Bool): Whether or not to drive component 
                                  with a scaleConstraint
        sub_ctrls (int): How many sub ctrls to add under main ctrl
        add_joint (str): valid inputs are ['follow','add','parentConstraint']

    """
    def __init__(self, common_args, component_args={} ):
        super(Static, self).__init__(common_args, component_args)

        # Private attributes
        self._output_name = None

        # Behavior
        self.scale_constrained = None
        self.tweak_ctrls = None
        self.add_joint = None
        self.output_xform = None
        
        # Interface
        self.ctr_shape = None
        self.ctr_size = None
        self.ctr_name = None
        self.ctr_full_name = None
        
    def configure(self):
        """
        """
        super(Static, self).configure()
        
        # Private attributes
        self._output_name = '{}_out_XFORM'.format(self.name)
        self._setteable_component_args = [
            'scale_constrained', 'tweak_ctrls','add_joint','ctr_shape'
        ]

        # Default values
        
        # Behavior
        self.scale_constrained = True
        self.tweak_ctrls = 0
        self.add_joint = 'follow'
        self.output_xform = None
        
        # Interface
        self.ctr_shape = 'square'
        self.ctr_size = 1
        self.ctr_name = self.name.replace('{}_'.format(self.side),'')
        self.ctr_full_name = '_'.join([self.side, self.ctr_name, 'CTR'])

    def add_ctrls_data(self):
        self.add_component_controler(
            ctr_data = {
                'name':self.ctr_name,
                'side':self.side,
                'shape':self.ctr_shape,
                'size':self.ctr_size,
                'position':self.position,
                'parent':self.ctrls_grp,
                'tweak_ctrls':self.tweak_ctrls,
                'add_joint': self.add_joint
            }
        )

    def setup_driver(self):
        """ Top node of ctrl is driven by main driver
        Uses parent and scale constraint to drive it (the scale constraint is
        optional)
        """
        super(Static, self).setup_driver()

        ctrl_top_node = self.ctrls[self.ctr_full_name].top_node

        self.main_driver.constrain(ctrl_top_node, 'parent', mo = True)
        
        if self.scale_constrained:
            self.main_driver.constrain(ctrl_top_node, 'scale', mo = True)

    def solve(self, template = False):
        """ Connects the lowest controls in the hierarchy 
        to the output transform
        """
        out_driver = self.ctrls[self.ctr_full_name].last_ctr

        self.output_xform = trans.Transform(
            name = self._output_name,
            side = self.side,
            parent = self.output_grp,
            match_object = out_driver
        )
        
        out_driver.constrain(self.output_xform, 'parent')
        
        if self.scale_constrained:
            out_driver.constrain(self.output_xform, 'scale')
