from ACtools.scripts.core import controls
from ACtools.scripts.core import dependency_graph as dg
from ACtools.scripts.core import transforms as trans

class Component(object):
	"""docstring for Component"""
	def __init__(self, common_args):
		
		if ('name' in common_args) and ('side' in common_args):
			self.side = common_args['side']
			self.name = '%s_%s' % (self.side,common_args['name'])
			
		else:
			raise Exception('Please provide name and side')

		#Empty attributes
		self.hierarchy_graph = dg.Dependency_graph(component_name = self.name)
		self.component_ctrls_data = {}
		self.ctrls = {}
		self.transforms = []

		self.ctrls_grp = '%s_ctrls_GRP' % self.name
		self.setup_grp = '%s_setup_GRP' % self.name
		self.skel_grp = '%s_skel_GRP' % self.name

		self.add_ctrls_data()

	def __str__(self):
		return self.name

	def add_ctrls_data(self):
		"""Only here to be overwritten by inheriting classes"""
		pass
	
	def setup_component_basics(self):
		self.ctrl_grp = trans.Transform(
			name = '%s_ctrls_GRP' % self.name
		)
		self.setup_grp = trans.Transform(
			name = '%s_setup_GRP' % self.name
		)

	def add_component_controler(self, control_data):
		""" Adds controller data to the __component_controls_data dictionary
		It also adds the controller to the hierarchy graph
		Args:
			control_data (dict) : Necessary data to add a controller
		"""
		
		ctr_name =  control_data['name']
		ctr_parent = control_data['parent']

		self.hierarchy_graph.add_node(ctr_name, ctr_parent)

		self.component_ctrls_data[ctr_name] = control_data

	def build_component(self):
		self.setup_component_basics()
		build_controls(self.hierarchy_graph.root_node, comp_obj = self)
			
	def solve(self, template=False):
		"""Adds the logic to the component
		Args:
			template (bool) : It changes the logic deppending on when the 
				component is being solved
		Returns:
			type: Description 
		"""
		pass
	
	def get_template_data(self):
		'''Queries transform data for controllers
		Transform data is in local space
		Returns:
			dict: keys are controller names. Entries are dictionaries
					containing transform data for each controller
		'''
		component_data = {}
		for ctr_name in self.ctrls.keys():
			ctr_obj = self.ctrls[ctr_name]
			ctr_data = {
				'transform':ctr_obj.get_transform(relative = True)
			}
			component_data[ctr_name] = ctr_data
		
		return component_data
		
@dg.travel_graph
def build_controls(graph_node, comp_obj = None):
	data = comp_obj.component_ctrls_data[str(graph_node)]

	new_ctr = controls.Control(
		name = data['name'],
		side = data['side'],
		shape = data['shape'],
		# size = data['size'],
		parent = data['parent'],
		# add_zero = data['add_zero'],
		# add_space = data['add_space']
	)

	comp_obj.ctrls[graph_node] = new_ctr