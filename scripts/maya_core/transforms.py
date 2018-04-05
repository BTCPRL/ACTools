import pymel.core as pm 
import maya.cmds as cmds

from CARF.scripts.maya_core import nodes
reload(nodes)
class Transform(nodes.Node):
	"""docstring for Transform"""
	def __init__(self, name, side=None, add_zero=False, add_space=False,
		parent=None, position=[0,0,0,0,0,0], match_object=False, 
		driver=None, node_type = 'transform'):
		
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
		
		#parent the node
		if parent:
			self.top_node.set_parent(parent)
		
		#set node's transforms
		self.top_node.set_position(position[:3], relative = True)
		if len(position) > 3:
			self.top_node.set_rotation(position[3:], relative = True)
		
		#Match object overrides any given transforms
		if match_object:
			pm.delete(pm.parentConstraint(match_object, self.top_node))
		
		if driver:
			self.top_node.constrain_to(driver, 'parent')

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
	no_mo = ['poleVector']
	args_str = ''
	for key in kwargs:
		value = kwargs[key]
		if type(value) is str:
			args_str = '{},{}="{}"'.format(args_str,key,value)
		else:
			args_str = '{},{}={}'.format(args_str,key,value)
	
	args_dict = kwargs
	if not constraint_type in no_mo:
		args_dict['mo']=mo
	command_str = 'new_constraint = pm.{}Constraint("{}","{}",**args_dict)'\
										.format(constraint_type,driver, driven)
	exec(command_str)

	if '{}.interpType'.format(new_constraint) in new_constraint.listAttr():
		new_constraint.setAttr('interpType', 2)
	
	return new_constraint



def create_parent_spaces(node, spaces_name, spaces_nodes, controller, default_spaces=[0,1], default_blend=0):
	
	#Create constrain from spaces to node
	cnst = node.constrain_to(spaces_nodes, constraint_type = 'parent', mo = 1)
	wals = [x.split('.')[-1] for x in cnst.getWeightAliasList()]
	#Add 2 (spaceA and spaceB) dropdown attributes in the controller plus one blend float attribute
	for i,s in enumerate(['A','B']):
		controller.attr_add(
			attr_name = 'space{}'.format(s),
			attr_type = 'enum',
			enums = spaces_name,
			default_value = default_spaces[i]
		)
	controller.attr_add(
		attr_name = 'blend',
		default_value = default_blend
	)
	#for each space:
	for i, space in enumerate(spaces_name):
	#	create 2 condition nodes (one for each dropdown attr)
		cond_a = nodes.Node(
			name = '{}_{}_space_A'.format(node,space), 
			node_type = 'condition',
		)
		cond_a.attr_set('secondTerm',i)
		cond_a.attr_set('colorIfFalseR',0)
		controller.attr_connect('spaceA', cond_a,'firstTerm')
		controller.attr_connectReverse('blend', cond_a,'colorIfTrueR')

		cond_b = nodes.Node(
			name = '{}_{}_space_B'.format(node,space), 
			node_type = 'condition',
		)
		cond_b.attr_set('secondTerm',i)
		cond_b.attr_set('colorIfFalseR',0)
		controller.attr_connect('spaceB', cond_b,'firstTerm')
		controller.attr_connect('blend', cond_b,'colorIfTrueR')

		space_add = nodes.Node(
			name = '{}_{}_space_val'.format(node,space),
			node_type = 'add'
		)
		cond_a.attr_connect('outColorR',space_add,'input1D[0]')
		cond_b.attr_connect('outColorR',space_add,'input1D[1]')

		space_add.attr_connect('output1D', cnst, wals[i])

	#	plug that sum into the corresponding weight alias of the constrain