from CARF.scripts.components import static
from CARF.scripts.maya_core import controls
from CARF.scripts.maya_core import transforms as trans

class Cog(static.Static):
	"""Cog component
	Has one ctrl, which could have tweak ctrls
	"""
	def __init__(self, common_args, component_args={}):
		super(Cog, self).__init__(common_args)

		# Private attributes
		self._output_name = '{}_out_XFORM'.format(self.name)

		# Default COG values
		self.ctr_shape = 'arrow_cross'

		if 'tweak_ctrls' not in component_args:
			self.tweak_ctrls = 1
		
		if 'position' not in common_args:
			self.position = [0,20,0,0,0,0]