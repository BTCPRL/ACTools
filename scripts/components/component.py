from CARF.scripts.maya_core import controls
from CARF.scripts.maya_core import joints
from CARF.scripts.maya_core import dependency_graph
from CARF.scripts.maya_core import transforms as trans

class Component(object):
	"""docstring for Component"""
	def __init__(self, common_args):
		""" TODO: lay out which component arguments are required and which ones
		are optional
		"""
		if not ('name' in common_args) and ('side' in common_args):
			raise Exception('Please provide name and side')
		if not 'type' in common_args:
			raise Exception('Please provide a component type')
		if 'driver' not in common_args and (common_args['type'] != 'root'):
			raise Exception('Please provide a driver')
		
		#Component common attributes
		self.side = common_args['side']
		self.name = '%s_%s' % (self.side,common_args['name'])
		self.position = [0,0,0,0,0,0]
		self.driver_target = False
		self.scale_driver_target = False

		#Getting user input
		if 'position' in common_args.keys():
			self.position = common_args['position']
			
		#Adding the drivers
		#Drivers come defined as component.node we need to split this data
		if common_args['type'] != 'root':
			try:
				self.driver_target = common_args['driver'].split('.')[1]
				self.driver_component = common_args['driver'].split('.')[0]
				#Scale drivers also need to be extracted
				if 'scale_driver' in common_args.keys():
					self.scale_driver_target =\
									common_args['scale_driver'].split('.')[1]
					self.scale_driver_component =\
									common_args['scale_driver'].split('.')[0]
			except IndexError:
				raise IndexError("Drivers must be defined using the"\
						" component name and the node name separated by '.'\n"\
						"Example: 'M_cog.M_cog_JNT'")
				
		self.hierarchy_graph = dependency_graph.Dependency_graph(
			graph_name = self.name)
		
		self.component_ctrls_data = {}
		self.template_data = None
		self.ctrls = {}
		self.transforms = []
		self.main_driver = None

		self.ctrls_grp = '%s_ctrls_GRP' % self.name
		self.setup_grp = '%s_setup_GRP' % self.name
		self.skeleton_grp = '%s_skeleton_GRP' % self.name
		self.driver_grp = '%s_driver_GRP' % self.name
		self.output_grp = '%s_output_GRP' % self.name


	def __str__(self):
		return self.name

	def add_ctrls_data(self):
		"""Needed(?) to be overwritten by inheriting classes"""
		pass
	
	def create_component_base(self):
		"""Creates common groups for all components
		
		These groups are provided as a mean to organize the different elements
		of every component.

		Each component's base hierarchy:
			CONTROLS_GRP
				[name]_ctrls_GRP
			SETUP_GRP
				[name]_setup_GRP
					[name]_driver_GRP
					[name]_output_GRP
					[name]_skeleton_GRP
		"""
		self.ctrls_grp = trans.Transform(
			name = '%s_ctrls_GRP' % self.name,
			parent = 'CONTROLS_GRP'
		)
		
		self.setup_grp = trans.Transform(
			name = '%s_setup_GRP' % self.name,
			parent = 'SETUP_GRP'
		)
		
		self.driver_grp = trans.Transform(
			name = '%s_driver_GRP' % self.name,
			parent = self.setup_grp
		)
		
		self.output_grp = trans.Transform(
			name = '%s_output_GRP' % self.name,
			parent = self.setup_grp
		)

		self.skeleton_grp = trans.Transform(
			name = '%s_skeleton_GRP' % self.name,
			parent = self.setup_grp
		)

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
					position (list) : [tx, ty, tz, rx, ry, rz] coordinates in
								world space
					parent (string) :  parent node. Default is self.ctrls_grp
					size (double) : Scale value for controler's shape. 
									Default is 1
					add_zero (bool) : Add a group above the controller. 
									Default is True
					add_space (bool) : Add a second group above the controller. 
									Default is True	
					add_joint (str): If a joint is needed, how will this 
									 joint follow the control?
		"""
		
		#Validation
		for needed_data in ['name','side','shape', 'parent']:
			if not needed_data in ctr_data.keys():
				raise Exception('Please provide %s for controler' % needed_data)
		
		#Joint data validation
		if 'add_joint' in ctr_data.keys():
			if ctr_data['add_joint'] in ['add','follow','parentConstraint']:
				pass
			else:
				raise Exception("When adding a controller joint, the only"\
					" available types are: ['add','follow','parentConstraint'")
		
		ctr_name =  '_'.join([ctr_data['side'], ctr_data['name'], 'CTR'])
		ctr_parent = ctr_data['parent'] 

		self.hierarchy_graph.add_node(ctr_name, ctr_parent)

		self.component_ctrls_data[ctr_name] = ctr_data

	def setup_driver(self):
		""" Connects each of the component's drivers to their respective master

		Each individual component is then responsible for connecting their own
		driver (or drivers) to all the elements that need to be driven

		TODO: Decide on whether or not to support the Dictionary option
		NOTE: Only the String option is supported for now
		self.driver_target can be a String or a Dictionary:
			In the first case, a single transform is created using
				the name "[name]_main_driver_GRP". 
			In the second case, each key in the dictionary must be a string 
				that will be used as a name for a new transform, which will 
				then be connected to it's respective value in the dictionary
		"""
		if self.driver_target:
			
			self.main_driver = trans.Transform(
				name = '%s_main_driver_XFORM' % self.name,
				parent = self.driver_grp
			)
			self.main_driver.constrain_to(
				self.driver_target, 
				'parent',  
				mo = False
			)
		
		if self.scale_driver_target:
			if self.scale_driver_target == self.driver_target:
				self.main_driver.constrain_to(
					self.driver_target,
					'scale',
					mo = True
				)
				self.main_scale_driver = self.main_driver
			else:
				self.main_scale_driver = trans.Transform(
					name = '%s_main_scale_driver_XFORM' % self.name,
					parent = self.driver_grp
				)
				self.main_scale_driver.constrain_to(
					self.scale_driver_target, 
					'parent',  
					mo = False
				)

	def build_template(self, template_data = None):
		"""
		"""
		self.create_component_base()
		if template_data:
			self.template_data = template_data
		self.template_grp = trans.Transform(
			name = '%s_template_GRP' % self.name,
			parent = 'TEMPLATE_GRP'
		)
		self.build_controls(self.hierarchy_graph.root_node, template = True)
		self.solve(template=True)

	def build_component(self):
		"""
		"""
		self.create_component_base()
		self.build_controls(self.hierarchy_graph.root_node)
		self.solve()
			
	def solve(self, template=False): 
		"""Adds the logic to the component
		Args:
			template (bool) : It changes the logic deppending on when the 
				component is being solved
		"""
		pass
	
	def get_template_data(self):
		"""Queries transform data for controlers
		
		Returns:
			dict: keys are controler names. Entries are dictionaries
					containing transform data for each controler
		"""
		component_data = {}
		for ctr_name in self.ctrls.keys():
			ctr_obj = self.ctrls[ctr_name]
			ctr_data = {
				'transform': ctr_obj.get_transform()
			}
			component_data[ctr_name] = ctr_data
		
		return component_data

	def finalize_component(self):
		"""TODO: Implement
		"""
		for grp in [self.ctrls_grp, self.skeleton_grp, self.setup_grp]:
			grp.attr_lock(['t','r','s','v'])
		
	@dependency_graph.travel_graph
	def build_controls(self, graph_node, template = False):
		""" Using the component data, builds a controler
		Private function, can't be accesed outside of component.py 
		Uses the @travel_graph decorator to create all the controlers of the given
		component 
		TODO: Should/could this be a method instead of a function?
		"""
		data = self.component_ctrls_data[str(graph_node)]
		
		#Data provided by default at 'add_component_controler' method
		ctr_name = data['name']
		ctr_side = data['side']

		#Check if ctrl needs a joint to constrain
		create_jnt = False
		if 'add_joint' in data.keys():
			if data['add_joint']:
				create_jnt = True
				joint_connection = data['add_joint']
			del(data['add_joint']) #Remove joint from data to avoid argument error

		#Validating template data
		if template:
			#Template stage specific behavior
			data['parent'] = self.template_grp
			data['ctr_type'] = 'template'
			
			if self.template_data:
				full_name = '_'.join([ctr_side, ctr_name, 'CTR'])
				data['position'] =  self.template_data[full_name]['transform']
		
		elif not self.template_data:
			raise Exception('No template data found for {}'.format(graph_node))
		
		else:
			full_name = '_'.join([ctr_side, ctr_name, 'CTR'])
			data['position'] =  self.template_data[full_name]['transform']
			
		#Creating the controler
		new_ctr = controls.Control(**data)
		#Dynamically adding the new ctr as an attribute for the component
		ctr_attr_name = '{}_{}_ctr'.format(ctr_side, ctr_name).lower()
		setattr(self, ctr_attr_name, new_ctr)
		self.ctrls[str(graph_node)] = new_ctr

		#Creating optional driven joint
		if create_jnt:
			#Get jnt name
			jnt_name = '{}_{}'.format(ctr_side, ctr_name)
			if 'CTR' == ctr_name.split('_')[-1]:
				jnt_name = ctr_name[:-4]
			
			#Create new joint
			new_jnt = joints.Joint(
				name = jnt_name,
				parent = self.skeleton_grp,
				match_object = new_ctr
			)
			
			#Dynamically adding the new joint as an attribute for the component
			jnt_attr_name = '{}_jnt'.format(jnt_name).lower()
			setattr(self, jnt_attr_name, new_jnt)
			if joint_connection in ['parentConstraint', 'follow']:
				new_ctr.last_ctr.constrain(new_jnt,'parent', mo = 0)
			if joint_connection == 'follow':
				new_ctr.last_ctr.constrain(new_jnt,'scale', mo = 0)
			if joint_connection == 'add':
				pass #Nothing happenss, joint is open for future connections