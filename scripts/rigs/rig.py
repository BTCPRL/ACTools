import imp 
import os


class Rig(object):
	"""docstring for Rig"""
	def __init__(self, asset_name):

		self.components = {}
		print "Rig basic stuff will happen"

		self.register( common_args = {
			'name': 'root',
			'side': 'M',
			'type' : 'root'
			},
			component_args = {
			'asset_name': asset_name.capitalize()
			}
		)
		self.root = self.components['M_root']
		self.root_settings = None


	def register(self, common_args, component_args={}):
		"""
		Creates a component object and adds it to the current rig
		"""
		component_type = common_args['type']
		component_name = common_args['name']
		#Dynamically imports and reload [component_type].py
		component_module = imp.load_source(
			'%s_module' % component_type,
			os.path.join('D:/Dev/ACtools/scripts/components','%s.py' % component_type)
		)
		component_class = getattr(component_module, component_type.capitalize())
		component_obj = component_class(common_args, component_args)

		self.components[component_obj.name] = component_obj
	
	def build_rig_template(self):
		'''Builds each component's template
		'''
		for comp_name in self.components.keys():
			self.components[comp_name].build_template()
	
	def create_rig_base(self):
		"""	Creates top groups for the rig
		parent groups are hard coded as they should be the same for every rig
		"""
		self.root_grp = trans.Transform(name = '%s_ROOT' % self.asset_name)
		self.ctrl_grp = trans.Transform(name = 'CONTROLS_GRP',
			parent = self.root_grp)
		self.setup_grp = trans.Transform(name = 'SETUP_GRP',
			parent = self.root_grp)
		self.skeleton_grp = trans.Transform(name = 'SKELETON_GRP',
			parent = self.root_grp)
	
	def extract_template_data(self):
		''' Creates a dictionary with each component's template data
		'''
		template_data = {}
		for comp_name in self.components.keys():
			template_data[comp_name] = 
				self.components[comp_name].get_template_data()
		print template_data
		
	def build_rig(self):
		print "Rig basic stuff will be built"
		