import pymel.core as pm 
import maya.cmds as cmds

class Node(object):
	"""
	Nodes class.

	Creates Node objects, storing the pymel object of the corresponding type
	"""
	def __init__(self, node_type, name='newNode', side=None):
		
		#Empty attributes for clarity of mind
		self.added_attributes = {}
		self.pm_node = None
		self.name = None
		self.node_type = node_type

		node_name = name
		if side:
			if not name.split('_')[0] == side:
				node_name = '%s_%s' % (side, name)
		
		#Supported types dictionary
		#Format: {name: [suffix, maya type]}
		supported_types = {
			#Utility nodes
			'remap':['_RMV', 'remapValue',],
			'clamp':['_CLP', 'clamp'],
			'multiply':['_MUL', 'multiplyDivide'],
			'divide':['_DIV', 'multiplyDivide'],
			'add':['_ADD', 'plusMinusAverage'],
			'substract':['_SUB', 'plusMinusAverage'],
			#Dag nodes
			'transform':['','transform'], #transforms get the suffix from name
			'control':['', 'transform'],
			'joint':['_JNT','joint'],
		}

		#Extract data from dictionary if possible
		if node_type in supported_types.keys():
			suffix = supported_types[node_type][0]
			node_name = '%s%s' % (node_name, suffix)
			maya_type = supported_types[node_type][1]
			
		else:
			maya_type = node_type

		#Create node
		self.name = node_name
		node = pm.createNode(maya_type, n = self.name)
		self.set_pm_node(node)

		

	def __repr__(self):
		return self.name
	
	def set_pm_node(self, node):
		if type (node) is list:
			self.pm_node = node[0]
		else:
			self.pm_node = node
	
	def duplicate(self, new_name):
		"""Returns a new node of the same type, with a new name"""
		return Node(self.node_type, new_name)

	"""Attribute methods"""

	def addAttr(self, attr_name, attr_type,default_value=None, min_val=None, 
		max_val=None, hidden=False, keyable=True, **Kwargs):
		""" Creates a new attribute """

		args = {
			'hidden':hidden,
			'keyable':keyable,
		}
		if default_value != None:
			args['dv'] = default_value

		if min_val != None:
			args['min'] = min_val
			args['hasMaxValue'] = True

		if max_val != None:
			args['max'] = max_val
			args['hasMinValue'] = True

		self.pm_node.addAttr(attr_name, at = attr_type, **args)
		pass

	def getAttr(self, attr_name):
		"""Returns attribute value"""
		return self.pm_node.getAttr(attr_name)

	def connectAttr(self, attr_name, target, force = False):
		"""Connects given attribute with target"""
		self.pm_node.connectAttr(attr_name, target, f = force)
		
	def attr_set(self, attr_name, value):
		"""Sets the specified attribute to the given value"""
		self.pm_node.setAttr(self.name, value)
	
	def attr_lock(self, attr_name, show=False):
		"""Locks the attribute"""
		self.attr_state(
			attr_name = attr_name, 
			keyable = False,
			lock = True, 
			show = show)
		
	def attr_unlock(self, attr_name, show=True):
		"""Unlocks the attribute"""
		self.attr_state(
			attr_name = attr_name, 
			keyable = True, 
			lock = False, 
			show = show)

	def attr_state(self, attr_name, keyable, lock, show):
		"""Changes the state of an attribute"""
		self.pm_node.setAttr(
			attr_name, 
			keyable = keyable, 
			lock = lock, 
			cb = show
		)


