from ACtools.scripts.components import component
from ACtools.scripts.core import controls
from ACtools.scripts.core import transforms as trans
reload(component)
class Root(component.Component):
	"""
	Root component.
	It carries the top groups information. Creates top level controller
	Different from other components in the sense that it has to be created first
	"""
	def __init__(self, common_args, component_args={}):
		super(Root, self).__init__(common_args)

		if 'asset_name' in component_args:
			self.asset_name = component_args['asset_name']
		else:
			raise Exception('Please provide an asset_name')

		#empty attributes

		self.asset_root = None
		self.asset_ctrl_grp = None
		self.asset_setup_grp = None
		self.asset_skel_grp = None

	def add_ctrls_data(self):
		self.add_component_controler(
			control_data = {
				'name':'root',
				'side':'M',
				'shape':'root',
				'parent':self.ctrls_grp
			}
		)

	def create_template_grps(self):
		"""	
		Creates top groups for the rig
		"""
		self.asset_root = trans.Transform(
				name = '%s_ROOT' % self.asset_name
			)
		# self.asset_ctrl_grp = trans.Transform(
		# 		name = 'CONTROLS_GRP',
		# 		parent = self.asset_root
		# 	)
		# self.asset_setup_grp = trans.Transform(
		# 		name = 'SETUP_GRP',
		# 		parent = self.asset_root
		# 	)
		# self.asset_skel_grp = trans.Transform(
		# 		name = 'SKELETON_GRP',
		# 		parent = self.asset_root
		# 	)
		self.template_grp = trans.Transform(
				name = 'TEMPLATE_GRP',
				parent = self.asset_root
			)
		pass

	def build_template(self):	
		self.ctrls = {}		
		self.create_template_grps()
		self.root_ctr = controls.Control(
				name = 'root',
				shape = 'root',
                parent=self.template_grp
			)
		self.ctrls[self.root_ctr.name] = self.root_ctr
		pass

	#This could be better, this is just hard coded and it would require 
	## constant updating of the code. Needs proper logic
	def get_template_data(self):
		""" Override component get_template_data
		Root will always be at origin

		Returns: (dict) template data for root, at origin
		"""
		root_template_data = {
			'M_root_CTR':{
				'transform':[0,0,0,0,0,0]
			}
		}
		return root_template_data
		
	# def build_component(self):
	# 	self.create_hierarchy_grps()
