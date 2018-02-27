import pymel.core as pm
import maya.cmds as cmds

class Attribute(object):
	"""docstring for Attribute"""
	def __init__(self, attr_name, attr_type, default_value=None, min_value=None, 
		max_value=None, hidden=False, keyable=True, **Kwargs):

		#Store values		
		self.name = attr_name
		self.type = attr_type
		self.default_value = default_value
		self.min_value = min_value
		self.max_value = max_value
		self.hidden = hidden
		self.keyable = keyable
		self.lock = False

		add(node = self, attr_name = attr_name, attr_type = attr_type,
			default_value = default_value, min_value = min_value, 
			max_value = max_value)
			
	def attr_lock(self, hidden=True):
		self.attr_state(keyable = False, lock = True, hidden=hidden)
		
	def attr_unlock(self, hidden=True):
		self.attr_state(keyable = True, lock = False, hidden=hidden)

	def attr_state(self, keyable, lock, hidden):
		self.keyable = keyable
		self.lock = lock
		self.hidden = hidden

		self.pmNode.setAttr(
			self.name, 
			keyable = keyable, 
			lock = lock, 
			cb = hidden
		)

	def attr_set(self, value):
		self.pmNode.setAttr(self.name, value)
	
def _add(node, attr_name, attr_type, default_value=0, min_value=0, 
	max_value=1, hidden=False, keyable=True, **Kwargs):

	args = {
		'hidden':hidden,
		'keyable':keyable,
		'dv': default_value,
		'min': min_value,
		'hasMinValue': True,
		'max': max_value,
		'hasMaxValue': True
	}
	args.update(Kwargs)

	return node.addAttr(attr_name, at = attr_type, **args)

def _set(node, attr_name, value, **Kwargs):
	"""TODO: docstring
	"""
	return node.setAttr(attr_name, value, Kwargs)

def _get(node, attr_name, **Kwargs):
	"""TODO: docstring
	"""
	return node.getAttr(attr_name, Kwargs)

def _lock(node, attr_name, hide=True, **Kwargs):
	"""TODO: docstring
	"""
	node.setAttr(attr_name, keyable = False, lock = True, cb = not hide)

def _unlock(node, attr_name, show=True, **Kwargs):
	"""TODO: docstring
	"""
	node.setAttr(attr_name, keyable = True, lock = False, cb = show)

def _link(node, attr_name, target_node, f=1):
	""" Connects the same attribute between two ndoes
	Assumes the same attribute is present in both nodes
	Args :  node : node that will drive the attr's value
			attr_name (str): common attribute to be linked between
			target_node : receiving node of the connection
	"""
	node.connectAttr(attr_name, '{}.{}'.format(target_node, attr_name), force=f)

def _connect(node, attr_name, target, f=1):
	"""TODO: docstring
	"""
	node.connectAttr(attr_name, target, force =f)