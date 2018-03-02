import pymel.core as pm 
import maya.cmds as cmds

from CARF.data import global_data as g_data
from CARF.scripts.maya_core import attributes

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
			if side not in g_data.positions_prefifx:
				raise Exception('side has to be one of the following: '\
					'%s' % g_data.positions_prefifx )
			if not name.split('_')[0] == side:
				node_name = '%s_%s' % (side, name)
		
		#Supported types dictionary
		#Format: {name: [suffix, maya type]}
		supported_node_types = {
			#Utility nodes
			'condition':['_COND', 'condition'], 
			'remap':['_RMV', 'remapValue',],
			'clamp':['_CLP', 'clamp'],
			'reverse':['_REV','reverse'],
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
		if node_type in supported_node_types.keys():
			suffix = supported_node_types[node_type][0]
			node_name = '%s%s' % (node_name, suffix)
			maya_type = supported_node_types[node_type][1]
			
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

	"""
	Attribute methods
		For more documentation and Args explanation, check attributes.py
	"""
	def attr_add(self, attr_name, attr_type='slider', default_value=0, 
		min_value=None, max_value=None, hidden=False, keyable=True, **Kwargs):
		""" Creates a new attribute """
		attributes._add(self.pm_node, attr_name, attr_type, default_value, 
								min_value, max_value, hidden, keyable, **Kwargs)

	def attr_get(self, attr_name, **Kwargs):
		"""Returns the attribute value"""
		return attributes._get(self.pm_node, attr_name, Kwargs)
		
	def attr_set(self, attr_name, value, **Kwargs):
		"""Sets the specified value in the given attribute"""
		attributes._set(self.pm_node, attr_name, value, Kwargs)
	
	def attr_lock(self, attr_name, hide=True, **Kwargs):
		"""Locks the attribute"""
		attributes._lock(self.pm_node, attr_name, hide, Kwargs)
		
	def attr_unlock(self, attr_name, show=True):
		"""Unlocks the attribute"""
		attributes._lock(self.pm_node, attr_name, show, Kwargs)
	
	def attr_connect(self, attr_name, target, target_attr, f=False):
		"""Connects given attribute with target"""
		attributes._connect(self.pm_node, attr_name, target, target_attr, f = f)

	def attr_link(self, attr_name, target, f=False):
		"""Links same attribute betwen targets"""
		attributes._link(self.pm_node, attr_name, target, f = f)
	
	def attr_connectReverse(self, attr_name, target, target_attr, f=False):
		"""Connects given attribute with target via reverse node"""
		attributes._connectReverse(self.pm_node, attr_name, target, target_attr,
																		  f = f)

	def attr_connectNegative(self, attr_name, target, target_attr, f=False):
		"""Connects the negative value of the given attribute with target"""
		attributes._connectNegative(self.pm_node, attr_name, target, 
															 target_attr, f = f)