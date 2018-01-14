import imp 
import os
from CARF.scripts.maya_core import transforms as trans

class Rig(object):
	"""docstring for Rig"""
	def __init__(self, builder, asset_name):

		self.builder = builder
		self.asset_name = asset_name

		#Empty attributes for clarity of mind
		self.components = {}
		
		self.root_grp = None
		self.geo_grp = None
		self.ctrls_grp = None
		self.setup_grp = None
		self.skeleton_grp = None
		
		self.base_grps = [self.root_grp, self.geo_grp, self.ctrls_grp, 
											self.setup_grp, self.skeleton_grp]

		self.root = self.initialize_component(
			common_args = {
				'name': 'root',
				'side': 'M',
				'type' : 'root'
				},
			component_args = {
				'asset_name': asset_name.capitalize()
			}
		)

		# self.build_base_grps()
		# self.root_settings = None

	def register(self, common_args, component_args={}):
		""" Intizializes and stores component object to the rig.
		"""
		component_obj = self.initialize_component(common_args, component_args)
		self.components[component_obj.name] = component_obj

	def initialize_component(self, common_args, component_args={}):
		""" Initializes a component object. 
		This will not add the component to the self.components dictionary
		Check component.py for information on common_args and component_args
		Args:
			common_args (dict) : Keyword arguments common to all components
			component_args (dict) : Keyword arguments specific to each type
		Returns:
			component: An instance of the specified component type 
		"""
		component_type = common_args['type']
		component_name = common_args['name']
		#Dynamically imports and reload [component_type].py
		component_module = imp.load_source(
			'%s_module' % component_type,
			os.path.join('D:/Dev/CARF/scripts/components','%s.py'\
															   % component_type)
		)
		component_class = getattr(component_module, component_type.capitalize())
		component_obj = component_class(common_args, component_args)

		return component_obj

	def build_rig_template(self):
		'''Builds each component's template
		'''
		for comp_name in self.components.keys():
			self.components[comp_name].build_template()
	
	def build_base_grps(self):
		"""	Creates top groups for the rig
		parent groups are hard coded as they should be the same for every rig
		"""
		#Root
		self.root_grp = trans.Transform(name = '%s_ROOT' % self.asset_name)

		grp_names = ['GEO_GRP', 'CONTROLS_GRP', 'SETUP_GRP', 'SKELETON_GRP']

		#Create all the other base groups and parent them under root
		for grp_var, name in zip(self.base_grps[1:], grp_names):
			grp_var = trans.Transform(name = name, parent = self.root_grp)

	
	def build_base(self):
		"""Wrapper for building base groups and root component
		"""
		self.build_base_grps()
		self.build_root()


	def build_root(self):
		"""Wrapper for build_component() call of self.root
		"""
		self.root.build_component()
	
	def extract_template_data(self):
		""" Creates a dictionary with each component's template data
		"""
		template_data = {}
		for comp_name in self.components.keys():
			template_data[comp_name] = \
								self.components[comp_name].get_template_data()
		print template_data
		
	def build(self):
		print "All components will be built"
		for comp_name in self.components.keys():
			self.components[comp_name].build_component()