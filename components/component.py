""" Provides common functionallity to all components, should be inherited. 

It contains the create method, which will dynamically create a component based
on a given type
"""
import importlib

from CARF.maya_core import controls
from CARF.maya_core import joints
from CARF.maya_core import dependency_graph
from CARF.maya_core import transforms as trans

class Component(object):
	"""docstring for Component"""

	def __init__(self, common_args, component_args={}):
		# Data storage
		self.common_args = common_args
		self.component_args = component_args #Component-type specific data
		
		#Component common attributes
		self.side = None
		self.name = None
		self.position = None
		self.create_settings_ctr = None
		self.settings_proxy = False
		
		#Private attributes
		#Dependency graph
		self._hierarchy_graph = None
		
		#Data for building
		self.component_ctrls_data = {}
		self.template_data = None
		
		#Contents
		self.ctrls = {}
		self.transforms = []
		self.settings = None
		
		#Drivers
		self.driver_target = None
		self.scale_driver_target = None
		self.settings_driver = None
		self.main_driver = None

		# Arguments that can be set by the user, specified in each component
		self._setteable_common_args = [
			'driver',
			'scale_driver',
			'settings_driver',
			'position'
		]
		self._setteable_component_args = []


		#Component top groups
		self.ctrls_grp = None
		self.setup_grp = None
		self.skeleton_grp = None
		self.driver_grp = None
		self.output_grp = None


	def __str__(self):
		return self.name

	def set_component_args(self):
		"""This is how a component reads the user input, it will only store
		arguments defined in _setteable_component_args, if an argument requires
		some logic before it can be stored, it shouldn't be part of this list
		and instead should be treated individually

		TODO:
			This setup renders the difference between common and component args
			kinda useless doesn't it??
		"""
		main_args = self._setteable_common_args
		comp_args = self._setteable_component_args
		user_args = main_args + comp_args
		for arg in user_args:
			if arg in self.component_args.keys():
				setattr(self, arg, self.component_args[arg])
			elif arg in self.common_args.keys():
				setattr(self, arg, self.common_args[arg])


	def configure(self):
		""" Sets the component's attributes based on the user input
		"""
		common_args = self.common_args
		
		#Common_args validation
		if not ('name' in common_args) and ('side' in common_args):
			raise Exception('Please provide name and side')
		
		#Component common attributes
		self.side = common_args['side']
		self.name = common_args['name']
		self.full_name = '_'.join([self.side, self.name])
		
		self.ctrls_grp = '%s_ctrls_GRP' % self.name
		self.setup_grp = '%s_setup_GRP' % self.name
		self.skeleton_grp = '%s_skeleton_GRP' % self.name
		self.driver_grp = '%s_driver_GRP' % self.name
		self.output_grp = '%s_output_GRP' % self.name

		self._hierarchy_graph = dependency_graph.Dependency_graph(
			graph_name = self.name)
		
		#Defaults
		self.position = [0,0,0,0,0,0]
		
		# Adding the drivers
		# Only the Root component can have no driver
		#TODO: What if driver-less components are actually allowed?
		if 'Root' not in str(type(self)):
			if 'driver' not in common_args:
				raise Exception('Please provide a driver')
			
			#Drivers come defined as component.node we need to split this data
			self.driver_target = common_args['driver']
			# self.driver_component = driver_full.split('.')[0]
			
			#Scale drivers also need to be extracted
			if 'scale_driver' in common_args.keys():
				self.scale_driver_target = common_args['scale_driver']

	def add_ctrls_data(self):
		"""This method should be overwritten by each component type """
		pass
	
	def add_jnts_data(self):
		"""This method should be overwritten by each component type """
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
			parent = 'CTRLS_GRP'
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
			parent = 'SKELETON_GRP'
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
		for required in ['name','side','shape', 'parent']:
			if not required in ctr_data.keys():
				raise Exception('Please provide %s for controler' % required)
		
		#Joint data validation
		if 'add_joint' in ctr_data.keys():
			if ctr_data['add_joint'] in ['add','follow','parentConstraint']:
				pass
			else:
				raise Exception("When adding a controller joint, the only"\
					" available types are: ['add','follow','parentConstraint'")
		
		ctr_name =  '_'.join([ctr_data['side'], ctr_data['name'], 'CTR'])
		ctr_parent = ctr_data['parent'] 

		self._hierarchy_graph.add_node(ctr_name, ctr_parent)

		self.component_ctrls_data[ctr_name] = ctr_data
	
	def add_component_jnt(self, jnt_data):
		""" TODO: implement, Docs

		idea:

		Require same thing as ctr_data requires. Also require a parent

		Optional args:
		ctr_driver (str): Ctr name to parent constraint to
		scale_driver (bool): If True and ctr_driver, jnt gets scale_constrained too

		Have a list of jnts per component, in order?
		Also need to be able to store the parent information for later

		Should this work with another hierarchy graph as well then?
		"""

		pass

	def setup_driver(self):
		""" Connects each of the component's drivers to their respective master

		Each individual component is then responsible for connecting their own
		driver (or drivers) to all the elements that need to be driven

		TODO: Decide on whether or not to support the Dictionary option
				No? Just one driver per component and special components have 
				an special component_arg for extra drivers?
				Only one driver seems to be the most common scenario
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
		self.build_controls(self._hierarchy_graph.root_node, template = True)
		self.solve(template=True)

	def build_component(self):
		"""
		"""
		self.create_component_base()
		self.build_controls(self._hierarchy_graph.root_node)
		self.solve()
			
	def setup_settings_ctr(self):
		""" Creates the settings ctr for the component
		This control will cointain attributes that will modify the behavior
		of the component. 
		TODO: 'proxy_Driver' has bigger implications than this
		If a "proxy_driver" is specified, no new control gets created
		"""

		if self.create_settings_ctr:

			self.settings = controls.Control(
				name='{}_settings'.format(self.name),
				parent=self.ctrls_grp,
				side=self.side,
				shape='settings',
				color='green'
			)

			driver = self.main_driver
			if self.settings_driver:
				driver = self.settings_driver
			self.settings.constrain_to(driver, 'parent', mo=False)
			self.settings.constrain_to(driver, 'scale', mo=False)
			self.settings.attr_lock(['t','r','s','v'])

	def add_setting(self, attr_name, attr_type='slider', **Kwargs):
		""" Shortcut to add an attribute to the settings ctrl
		TODO: better docs, expand implementation?
		"""
		self.settings.attr_add(
			attr_name=attr_name,
			attr_type=attr_type,
			**Kwargs
		)

	def assemble_skeleton(self):
		""" TODO: Docs, implement

		idea:
			For each jnt in self.jnts.... find their parent and parent it?
			This is useless for all joints except the first one if the 
			hierarchy graph is used... unless components with no 'top_jnt' are
			allowed, in that case hierarchy graph is not needed when creating
			the jnts
		"""
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
		Uses the @travel_graph decorator to create all the controlers of the 
		given component 
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
		ctr_attr_name = '{}_{}_CTR'.format(ctr_side, ctr_name)
		setattr(self, ctr_attr_name, new_ctr)
		# NOTE: Adding these attributes capitalized goes against convention, 
		# but it will be confusing to use the same name in lowercase for some
		#  cases and capitalized for other
		self.ctrls[str(graph_node)] = new_ctr

		#Creating optional driven joint
		if create_jnt:
			new_jnt = joints.Joint(
				name = ctr_name,
				side = ctr_side,
				parent = self.skeleton_grp,
				match_object = new_ctr
			)
			
			#Dynamically adding the new joint as an attribute for the component
			setattr(self, new_jnt.full_name, new_jnt)

			if joint_connection in ['parentConstraint', 'follow']:
				new_ctr.last_ctr.constrain(new_jnt,'parent', mo = 0)
			
			if joint_connection == 'follow':
				new_ctr.last_ctr.constrain(new_jnt,'scale', mo = 0)
			
			if joint_connection == 'add':
				pass #Nothing happenss, joint is open for future connections

def create(component_type, common_args, component_args={}):
	""" Dynamically loads a specific component module, gets the class and 
	instanciates an object
	Args:
		component_type (str): Type of component that is going to be created
		common_args (dict) : Keyword arguments common to all components
		component_args (dict) : Keyword arguments specific to each type
	
	Returns:
		component: An instance of the specified component type 
	"""
	relative_module = '.'+component_type

	component_module = importlib.import_module(relative_module, 
											   package=__package__)

	Component_class = getattr(component_module, component_type.capitalize())

	component_obj = Component_class(common_args, component_args)
	
	return component_obj