import pymel.core as pm 
import maya.cmds as cmds

from CARF.scripts.maya_core import nodes


class Transform(nodes.Node):
	"""docstring for Transform"""
	def __init__(self, name, side=None, add_zero=False, add_space=False,
		parent=None, position=[0,0,0,0,0,0], node_type='transform'):
		
		#Args validation
		suffix = name.split('_')[-1]
		if len(name.split('_')) < 2 or suffix.islower():
			raise Exception('Transfroms need a suffix in the name.'\
				' Suffix should be all upper case')
		if len(position) > 6:
			raise Exception('Position has to be of the form [tx,ty,tz] or '\
				'[tx,ty,tz,rx,ry,rz]')

		super(Transform, self).__init__(node_type = node_type, name = name,
			side = side)
		
		#Empty attributes for clarity of mind
		self.top_node = None
		self.zero = None
		self.space = None
		self.parent = None

		self.constraints = []

		#Set up groups above ctrl
		self.top_node = self
		
		if add_zero:
			self.zero = Transform(
					name = self.name.replace(suffix,'ZERO'),
					side = side
			)
			self.set_top_node(self.zero)

		if add_space:
			self.space = Transform(
				name = self.name.replace(suffix,'SPACE'),
				side = side
			)
			self.set_top_node(self.space)

		if parent:
			self.top_node.set_parent(parent)
		
		self.top_node.set_position(position[:3], relative = True)
		if len(position) > 3:
			self.top_node.set_rotation(position[3:], relative = True)

	def set_parent(self, parent):
		if not parent:
			raise Exception('%s is not a valid parent' % parent)
		self.parent = parent
		self.pm_node.setParent(parent)
	
	def set_top_node(self, node):
		temp = self.top_node
		pm.parent(temp, node)
		self.top_node = node

	#TODO: This 2 methods are almost the same, try to merge them
	def constrain(self, target, constraint_type, mo = 1, **kwargs):
		"""Constrains target or targets to current transform
		For more information read _constrain Documentation
		Returns:
			list : new created constraint(s)
		"""
		target_list = target if type(target) is list else [target]
		constraints_list = []
		if constraint_type == 'aim' and len(target_list) > 1:
			raise Exception('Aim constraints only support 1 target')
		for t in target_list:
			new_constraint = _create_maya_constrain(
				driver = self, 
				driven = t, 
				constraint_type = constraint_type,
				mo = mo,
				**kwargs
			)
			# t.constraints.append(new_constraint)
			#TODO: figure out if you are getting your transform class or a regular maya transform

		return new_constraint
		
	def constrain_to(self, target, constraint_type, mo = 1, **kwargs):
		"""Constrains self to given target or targets
		For more information read _constrain Documentation
		Returns:
			list : new created constraint(s)
		"""
		target_list = target if type(target) is list else [target]
		constraints_list = []
		if constraint_type == 'aim' and len(target_list) > 1:
			raise Exception('Aim constraints only support 1 target')
		for t in target_list:
			new_constraint = _create_maya_constrain(
				driver = t, 
				driven = self, 
				constraint_type = constraint_type,
				mo = mo,
				**kwargs
			)
		self.constraints.append(new_constraint)

		return new_constraint

	def get_transform(self, relative = False):
		'''Description
		Args:
			relative (boolean) : True object space values
		Returns:
			list : [tX,tY,tZ,rX,rY,rZ] translation and rotation values
		'''
		return self.get_position(relative) + self.get_rotation(relative)

	def get_position(self, relative = False):
		'''Returns wolrd space or local space translation of object
		Args:
			relative (boolean) : True if looking for translation in object space
		Returns:
			list: [X,Y,Z] translation values for object in wolrd/local space
		'''
		space = 'object' if relative else 'world'
		return list(self.pm_node.getTranslation(space))
		
	def get_rotation(self, relative = False):
		'''Returns wolrd space or local space rotation of object
		Args:
			relative (boolean) : True if looking for rotation in object space
		Returns:
			list: [X,Y,Z] rotation values for object in wolrd/local space
		'''
		space = 'object' if relative else 'world'
		return list(self.pm_node.getRotation(space))

	def get_scale(self,scale):
		'''Gets object's scale
		Returns:
			list : [X,Y,Z] values for object's scale
		'''
		self.pm_node.getScale(scale)

	def set_position(self,position, relative = False):
		''' Sets object's position in space (either wolrd or local)
		Args:
			position (list) : 
				space coordinates in which to move the object [tX,tY,tZ] 
			relative (boolean): True if position is in object Space
		'''
		space = 'object' if relative else 'world'
		self.pm_node.setTranslation(position,space)
	
	def set_rotation(self,rotation, relative = False):
		''' Sets object's rotation in space (either wolrd or local)
		Args:
			rotation (list) : 
				space coordinates in which to move the object [tX,tY,tZ] 
			relative (boolean): True if rotation is in object Space
		'''
		space = 'object' if relative else 'world'
		self.pm_node.setRotation(rotation,space)

	def set_scale(self,scale):
		''' Sets object's scale
		Args:
			scale (list) : [X,Y,Z] values for object's scale
		'''
		self.pm_node.setScale(scale)
	
	
def _create_maya_constrain(driver, driven, constraint_type, mo=1, **kwargs):
	""" Constrains driven to driver. Using each transform's pmNode
	Args:
		constraint_type (str) : Type of constraint to be created. 
			Supported values for constraint_type:
				['parent','point','orient','scale', 'aim']
		driver (transform) : Maya's group that will drive the action
		driven (transform) : Maya's group that will follow the driver's action
		mo (bool) : keep offset boolean
		kwargs : Other arguments needed for each type of coinstrain
	Returns:
		(pymel constraint): Pymel's contraint object
	"""
	args_str = ''
	for key in kwargs:
		args_str = args_str + key +' = '+kwargs[key]

	command_str = 'new_constraint = pm.%sConstraint("%s","%s",mo = %s,%s)'\
								% (constraint_type, driver, driven,mo, args_str)
	exec(command_str)

	if '{}.interpType'.format(new_constraint) in new_constraint.listAttr():
		new_constraint.setAttr('interpType', 2)
	
	return new_constraint



def create_parent_spaces(node, spaces_name, spaces_nodes, controller, default_spaces=[0,1], default_blend=0):
	
	#Create constrain from spaces to node
	node.constrain_to(spaces_nodes, constraint_type = 'parent', mo = 1)
	#Add 2 (spaceA and spaceB) dropdown attributes in the controller plus one blend float attribute
	for i,s in enumerate(['A','B']):
		controller.add_attr(
			name = 'space{}'.format(s),
			attr_type = 'enum',
			enum_list = spaces_name,
			dv = default_spaces[i]
		)
	controller.add_attr(
		name = 'blend',
		attr_type = 'float',
		dv = default_blend
	)
	#for each space:
	for i, space in enumerate(spaces_name):
	#	create 2 condition nodes (one for each dropdown attr)
		cond_a = nodes.Node(
			name = '{}_A'.format(space), 
			node_type = 'condition',
		)

	#	make an inverse connection from blend attr to color if true of first condition

	#	make a direct connection from blend attr to color if true of second condition

	#	add the result of each condition

	#	plug that sum into the corresponding weight alias of the constrain