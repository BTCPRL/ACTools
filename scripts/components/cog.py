from CARF.scripts.components import component
from CARF.scripts.maya_core import controls
from CARF.scripts.maya_core import transforms as trans

class Cog(component.Component):
	"""Cog component
	Has one ctrl, which could have tweak ctrls
	"""
	def __init__(self, common_args, component_args={}):
		super(Cog, self).__init__(common_args)

		# Private attributes
		self._output_name = '{}_out_XFORM'.format(self.name)

		# Default values
		self.scale_constrained = True
		self.output_xform = None

		# Getting user input
		self.ctrl_name = common_args['name']
		self.ctr_full_name = '_'.join([self.side, self.ctrl_name, 'CTR'])

		# List of arguments that can be set by the user
		setteable_component_args = [
			'scale_constrained'
		]

		# Getting component args
		for arg in component_args.keys():
			if arg in setteable_component_args:
				setattr(self, arg, component_args[arg])

		
	def add_ctrls_data(self):
		self.add_component_controler(
			ctr_data = {
				'name':self.ctrl_name,
				'side':self.side,
				'shape':'arrow_cross',
				'position':[0,25,0,0,0,0],
				'parent':self.ctrls_grp,
				'add_joint':'follow'
			}
		)

	def setup_driver(self):
		""" Single ctrl driven by main driver
		Uses parent and scale constraint to drive it
		"""
		super(Cog, self).setup_driver()

		ctrl_top_node = self.ctrls[self.ctr_full_name].top_node

		self.main_driver.constrain(ctrl_top_node, 'parent', mo = True)
		
		if self.scale_constrained:
			self.main_driver.constrain(ctrl_top_node, 'scale', mo = True)

	def solve(self):
		""" Connects ctrl to output transform
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
