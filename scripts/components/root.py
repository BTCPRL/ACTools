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
			'local_tweaks' (int): Number of ctrls under the root (default 1)
	"""
	def __init__(self, common_args, component_args={}):
		super(Root, self).__init__(common_args, component_args)
		# Private attributes
		self._output_name = None
		
		# Root attributes
		self.asset_name = None
		self.local_tweaks = None
		self.output_xform = None


	def configure(self):
		"""
		"""
		super(Root, self).configure()

		# Args Validation 
		if 'asset_name' in self.component_args.keys():
			self.asset_name = self.component_args['asset_name']
		else:
			raise Exception('Please provide an asset_name')
		
		# Private attributes
		self.template_data = self.get_template_data()
		self._output_name = '{}_out_XFORM'.format(self.name)
		self._setteable_component_args = [
			'local_tweaks'
		]
		
		# Default values
		self.local_tweaks = 0
		self.create_settings_ctr = True
		self.settings_driver = 'M_root_JNT'

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
				'tweak_ctrls': self.local_tweaks
			}
		)
		# sub_ctrl_size = 1
		# size_decrement = 1 / float(self.local_tweaks + 1)

		# last_ctr = 'M_root_CTR'
		# for i in range(self.local_tweaks):
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

		# Constrain skeleton
		last_ctr_obj.constrain(self.m_root_jnt, 'parent')
		last_ctr_obj.constrain(self.m_root_jnt, 'scale')

		# Create and constrain transforms output
		self.output_xform = trans.Transform(
			name = self._output_name,
			side = self.side,
			parent = self.output_grp
		)

		last_ctr_obj.constrain(self.output_xform, 'parent', mo = False)
		last_ctr_obj.constrain(self.output_xform, 'scale', mo = False)


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

	def setup_settings_ctr(self):
		""" Adds attributes to interact with different parts of the rig
		"""

		super(Root, self).setup_settings_ctr()

		#Title, the asset name, this provides no functionality 
		self.settings.attr_add(
				attr_type='header',
				header_val=self.asset_name.upper(),
			)

		#Vis toggles for main rig groups
		for attr in ['ctrlVis','geoVis','jntsVis', 'setupVis']:
			self.settings.attr_add(
				attr,
				'bool',
				default_value=1,
				hidden=False,
				keyable=False
			)
		
		#Toggle for selecting the geo
		self.settings.attr_add(
				'geoSelect',
				'bool',
				default_value=0,
				hidden=False,
				keyable=False
			)