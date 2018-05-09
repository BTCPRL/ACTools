from CARF.scripts.maya_core import controls
from CARF.scripts.maya_core import dependency_graph
from CARF.scripts.maya_core import transforms as trans

class Component(object):
	"""docstring for Component"""
	def __init__(self, common_args):
		
		if ('name' in common_args) and ('side' in common_args):
			self.side = common_args['side']
			self.name = '%s_%s' % (self.side,common_args['name'])
			
		else:
			raise Exception('Please provide name and side')

		#Empty attributes
		self.hierarchy_graph = dependency_graph.Dependency_graph(component_name = self.name)
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
		"""Needs(?) to be overwritten by inheriting classes"""
		pass
	
	def create_component_base(self):
		"""TODO: Docstring
		"""
		self.ctrls_grp = trans.Transform(
			name = '%s_ctrls_GRP' % self.name,
			parent = 'CONTROLS_GRP'
		)
		self.ctrls_grp.attr_lock(['t','r','s','v'])
		
		self.setup_grp = trans.Transform(
			name = '%s_setup_GRP' % self.name,
			parent = 'SETUP_GRP'
		)
		self.setup_grp.attr_lock(['t','r','s','v'])
		
		self.skeleton_grp = trans.Transform(
			name = '%s_skeleton_GRP' % self.name,
			parent = 'SKELETON_GRP'
		)
		self.skeleton_grp.attr_lock(['t','r','s','v'])

	def add_component_controler(self, ctr_data):
		""" Adds controler data to the __component_controls_data dictionary
		It also adds the controler to the hierarchy graph
		Args:
			ctr_data (dict) : Data to add a controler
				Data required:
					name (string) : controler description
					side (string) : one option from g_data.positions_prefifx
					shape (string) : name of which shape to use
				
				Optional data:
					parent (string) :  parent node. Default is self.ctrls_grp
					size (double) : Scale value for controler's shape. 
									Default is 1
					zero (bool) : Add a group above the controller. 
									Default is True
					space (bool) : Add a second group above the controller. 
									Default is True	
		"""
		
		#Validation
		for needed_data in ['name','side','shape']:
			if not needed_data in ctr_data.keys():
				raise Exception('Please provide %s for controler' % needed_data)
		
		ctr_name =  ctr_data['name']
		ctr_parent = ctr_data['parent'] 

		self.hierarchy_graph.add_node(ctr_name, ctr_parent)

		self.component_ctrls_data[ctr_name] = ctr_data

	def build_component(self):
		self.create_component_base()
		build_controls(self.hierarchy_graph.root_node, comp_obj = self)
			
	def solve(self, template=False): 
		"""Adds the logic to the component
		Args:
			template (bool) : It changes the logic deppending on when the 
				component is being solved
		"""
		pass
	
	def get_template_data(self):
		'''Queries transform data for controlers
		Transform data is in local space
		Returns:
			dict: keys are controler names. Entries are dictionaries
					containing transform data for each controler
		'''
		component_data = {}
		for ctr_name in self.ctrls.keys():
			ctr_obj = self.ctrls[ctr_name]
			ctr_data = {
				'transform': ctr_obj.get_transform(relative = True)
			}
			component_data[ctr_name] = ctr_data
		
		return component_data

	def finalize_component(self):
		"""TODO: Implement
		"""
		pass
		
@dependency_graph.travel_graph
def build_controls(graph_node, comp_obj = None):
	""" Using the component data, builds a controler
	Private function, can't be accesed outside of component.py 
	Uses the @travel_graph decorator to create all the controlers of the given
	component 
	"""

	data = comp_obj.component_ctrls_data[str(graph_node)]
	#Data provided by default at 'add_component_controler' method
	ctr_name = data['name']
	ctr_side = data['side']
	ctr_shape = data['shape']
	#Optional data
	ctr_size = data['size'] if 'size' in data.keys() else 1
	ctr_parent = data['parent'] if 'parent' in data.keys() else self.ctrls_grp
	ctr_add_zero = data['zero'] if 'zero' in data.keys() else True
	ctr_add_space = data['space'] if 'space' in data.keys() else True

	#Creating the controler
	new_ctr = controls.Control(
		name = ctr_name,
		side = ctr_side,
		shape = ctr_shape,
		size = ctr_size,
		parent = ctr_parent,
		add_zero = ctr_add_zero,
		add_space = ctr_add_space
	)

	comp_obj.ctrls[str(graph_node)] = new_ctr