import sys
import imp 
import os

from CARF.scripts.maya_core import dependency_graph
from CARF.scripts.maya_core import transforms as trans
from CARF.scripts.components import component

class Rig(object):
	"""docstring for Rig"""
	def __init__(self, asset_name):

		self.asset_name = asset_name

		#Private attributes
		self._components_list = []

		#Empty attributes for clarity of mind
		self.components = {}
		self.template_data = None
		self.root_grp = None
		self.root_ctr = None
		self.geo_grp = None
		self.ctrls_grp = None
		self.setup_grp = None
		self.skeleton_grp = None
		self.base_grps = ['root_grp', 'geo_grp', 'ctrls_grp', 
						  'setup_grp', 'skeleton_grp']

		self.root = component.create(
			component_type = 'root',
			common_args = {
				'name': 'root',
				'side': 'M',
				# 'type' : 'root'
			},
			component_args = {
				'asset_name': asset_name.capitalize()
			}
		)

		self.dependency_graph = None
		# self.build_base_grps()
		# self.root_settings = None
	
	def add_component(self, component_type, common_args, component_args={}):
		""" Intizializes and stores component object in the rig.
		This will not configure the component, just creates the instance
		"""
		#Instancing the component
		component_obj = component.create(
			component_type, 
			common_args, 
			component_args
		)
		self._components_list.append(component_obj)

		return component_obj
	
	def configure_rig(self):
		""" Configures components and creates dependency graph 
		Configures the root component before creating the dependency graph, 
		It then proceeds to configure each individual component

		If a rig were to need user-level input, it would be read here
		"""
		#Root comp configuration
		self.root.configure()
		self.root.add_ctrls_data()

		#Creating the dependency graph, and adding the root as a base
		self.dependency_graph = dependency_graph.Dependency_graph(
			graph_name = self.asset_name,
			graph_root_name = self.root.name
		)

		#Configuring the rest of the components and populating dependency graph
		for comp in self._components_list:
			#Setting up (or configuring) the component
			comp.configure()
			comp.set_component_args()
			comp.add_ctrls_data()
			self.components[comp.name] = comp
			
			#Adding the component to the dependency graph
			self.dependency_graph.add_node(
				node_name = comp.name,
				node_parent = comp.driver_component
			)
			

	def set_template_data(self, data):
		""" Saves data into rig.template_data attribute
		It also assigns each component it's own template data
		"""
		self.template_data = data
		for comp, comp_data in data.iteritems():
			if comp in self.components.keys():
				self.components[comp].template_data = comp_data
		
	def build_template(self):
		'''Builds each component's template
		'''
		self.template_grp = trans.Transform(
			name = 'TEMPLATE_GRP'
		)
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
			grp = trans.Transform(name = name, parent = self.root_grp)
			setattr(self,grp_var,grp)

	@dependency_graph.travel_graph
	def assemble_components(self, comp_graph_node):
		comp_name = str(comp_graph_node)
		if comp_name != 'M_root':
			
			self.components[comp_name].build_component()
			self.components[comp_name].setup_driver()

	def build(self):
		"""This method will be overwritten in each rig type
		This definition is to avoid crashing for rig types without build method
		"""
		pass

	def build_root(self):
		"""Wrapper for build_component() call of self.root
		"""
		self.root.build_component()
		self.root_ctr = self.root.ctrls['M_root_CTR']


	def final_touches(self):
		"""
		"""
		to_hide = [self.setup_grp, self.skeleton_grp]
		for grp in self.base_grps:
			grp_obj = getattr(self, grp)
			if grp_obj in to_hide:
				pass
				# grp_obj.attr_set('v',0) #TODO: bring when settings ctrl added
			grp_obj.attr_lock(['t','s','r','v'])
		self.geo_grp.attr_set('overrideEnabled',1)
		self.geo_grp.attr_set('overrideDisplayType',2)
		for comp_name in self.components.keys():
			self.components[comp_name].finalize_component()