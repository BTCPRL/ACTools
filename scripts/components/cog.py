from CARF.scripts.components import component
from CARF.scripts.maya_core import controls
from CARF.scripts.maya_core import transforms as trans
reload(component)
class Cog(component.Component):
	"""Cog component
	"""
	def __init__(self, common_args, component_args={}):
		self.ctrl_name = common_args['name']
		super(Cog, self).__init__(common_args)

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
