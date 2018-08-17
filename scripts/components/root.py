from CARF.scripts.components import component
from CARF.scripts.maya_core import controls
from CARF.scripts.maya_core import transforms as trans

class Root(component.Component):
	"""
	Root component.
	It carries the top groups information. Creates top level controlers and 
	settings ctrl

	Different from other components in the sense that it has to be created
	before any other component
	
	Args:
		component_args (dict):
			'asset_name' (str): Asset's name, this is REQUIRED
			'local_ctrls' (int): Number of ctrls under the root (default 1)
	"""
	def __init__(self, common_args, component_args={}):
		super(Root, self).__init__(common_args)

		# Args Validation 
		if 'asset_name' in component_args.keys():
			self.asset_name = component_args['asset_name']
		else:
			raise Exception('Please provide an asset_name')
		
		# Private attributes
		self.template_data = self.get_template_data()
		
		# Default values
		self.local_ctrls = 1

		# List of arguments that can be set by the user
		setteable_component_args = [
			'local_ctrls'
		]

		# Getting component args
		for arg in component_args.keys():
			if arg in setteable_component_args:
				setattr(self, arg, component_args[arg])

	def add_ctrls_data(self):
		self.add_component_controler(
			ctr_data = {
				'name':'root',
				'side':'M',
				'color':'dark_red',
				'shape':'root',
				'parent':self.ctrls_grp,
				'add_joint':'add'
			}
		)

		self.add_component_controler(
			ctr_data = {
				'name':'local',
				'side':'M',
				'size': 0.8,
				'color':'dark_yellow',
				'shape':'arrow',
				'parent':'M_root_CTR',
				'tweak_ctrls': self.local_ctrls
			}
		)
		# sub_ctrl_size = 1
		# size_decrement = 1 / float(self.local_ctrls + 1)

		# last_ctr = 'M_root_CTR'
		# for i in range(self.local_ctrls):
		# 	ctrl_number = '' if not i else '_{}'.format(i+1)
		# 	ctr_name = 'local{}'.format(ctrl_number)
		# 	self.add_component_controler(
		# 		ctr_data = {
		# 			'name': ctr_name,
		# 			'side': 'M',
		# 			'color': 'dark_yellow',
		# 			'shape': 'arrow',
		# 			'size': sub_ctrl_size,
		# 			'add_zero': False,
		# 			'add_space': False,
		# 			'parent': last_ctr,
		# 		}
		# 	)
		# 	sub_full_name = 'M_{}_CTR'.format(ctr_name)
		# 	last_ctr = sub_full_name
		# 	sub_ctrl_size-= size_decrement

		# self._last_ctr = last_ctr
	
	def solve(self):
		""" Will constraint the root jnt to the last ctrl
		"""
		last_ctr_obj = self.m_local_ctr.last_ctr
		last_ctr_obj.constrain(self.m_root_jnt, 'parent')
		last_ctr_obj.constrain(self.m_root_jnt, 'scale')

	# def create_template_grps(self):
	# 	"""	Creates top group where template controls will be parented under
	# 	"""
	# 	self.template_grp = trans.Transform(
	# 			name = 'TEMPLATE_GRP'
	# 		)
	# 	pass

	# def build_template(self):	
	# 	self.ctrls = {}		
	# 	self.create_template_grps()
	# 	self.root_ctr = controls.Control(
	# 			name = 'root',
	# 			shape = 'root',
    #             parent=self.template_grp
	# 		)
	# 	self.ctrls[self.root_ctr.name] = self.root_ctr
	# 	pass

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
			},
			'M_local_CTR':{
				'transform':[0,0,0,0,0,0]
			}
		}
		return root_template_data
		
	# def build_component(self):
	# 	self.create_hierarchy_grps()
