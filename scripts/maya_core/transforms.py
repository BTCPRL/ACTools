import pymel.core as pm 
import maya.cmds as cmds

from ACtools.scripts.maya_core import nodes
reload(nodes)


class Transform(nodes.Node):
	"""docstring for Transform"""
	def __init__(self, name, side, add_zero=False, add_space=False,
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

	def get_transform(self, relative = False):
		'''Description
		:Args:
			relative (boolean) : True object space values
		Returns:
			list : [tX,tY,tZ,rX,rY,rZ] translation and rotation values
		'''
		return self.get_position(relative) + self.get_rotation(relative)
	

	def get_position(self, relative = False):
		'''Returns wolrd space or local space translation of object
		:Args:
			relative (boolean) : True if looking for translation in object space
		Returns:
			list: [X,Y,Z] translation values for object in wolrd/local space
		'''
		space = 'object' if relative else 'world'
		return list(self.pm_node.getTranslation(space))
		
	def get_rotation(self, relative = False):
		'''Returns wolrd space or local space rotation of object
		:Args:
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
		:Args:
			position (list) : 
				space coordinates in which to move the object [tX,tY,tZ] 
			relative (boolean): True if position is in object Space
		'''
		space = 'object' if relative else 'world'
		self.pm_node.setTranslation(position,space)
	
	def set_rotation(self,rotation, relative = False):
		''' Sets object's rotation in space (either wolrd or local)
		:Args:
			rotation (list) : 
				space coordinates in which to move the object [tX,tY,tZ] 
			relative (boolean): True if rotation is in object Space
		'''
		space = 'object' if relative else 'world'
		self.pm_node.setRotation(rotation,space)

	def set_scale(self,scale):
		''' Sets object's scale
		:Args:
			scale (list) : [X,Y,Z] values for object's scale
		'''
		self.pm_node.setScale(scale)
	
	
	
	
	
