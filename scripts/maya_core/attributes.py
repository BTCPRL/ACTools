import pymel.core as pm
import maya.cmds as cmds

# from CARF.scripts.maya_core import nodes
"""
Module to manage creation, editing and connecting of Maya attributes.

All the methods are meant to only be accesed from the Nodes class, even though
they are accesible from any other class as well.

Common arguments for all functions:
	node (PyNode) : source node
	attr_name (str) : attribute belonging to node
"""

def _add(node, attr_name, attr_type='slider', default_value=0, min_value=None, 
	max_value=None, hidden=False, keyable=True, enums = [], **Kwargs):
	""" Creates a new attribute
	Args : 
		attr_type (str) : description of the attribute's functionality.
					valid values are: [
						'float' : numeric value with decimals,
						'long' : numeric value without decimals,
						'slider' : 'float' attribute with range [0,1] (Default),
						'bool' : a 'long' attribute with range [0,1],
						'enum' : dropdown list of str
					]
		default_value : starting value for the attribute
		min_value : lowest possible value the attribute will support
		max_value : biggest possible value the attribute will support
		hidden (bool) : decides if attribute will be visible in the channel box
		keyable (bool) : decides if new attribute can be animated or not
		enums (list of str) : string representation of the possible options
	"""
	#Base arguments to create a Maya attribute
	args = {
		'hidden':hidden,
		'keyable':keyable,
		'dv': default_value
	}
	
	#setting min and max value to accomodate for custom types
	min_v = 0 if attr_type in ['slider','bool'] else min_value
	max_v = 1 if attr_type in ['slider','bool'] else max_value

	if min_v != None:
		args.update({'min': min_v,'hasMinValue': True})
	if max_v != None:
		args.update({'max': max_v,'hasMaxValue': True})

	#If enum type, add enum list to args
	if attr_type == 'enum':
		args['en'] = ':'.join(enums)
	
	#Changing from custom types to maya's equivalent type for the attributes
	if attr_type in ['float','slider']:
		maya_type = 'double'
	elif attr_type == 'bool':
		maya_type = 'long'
	else:
		maya_type = attr_type
	
	#Adding Kwargs
	args.update(Kwargs)

	return node.addAttr(attr_name, at = maya_type, **args)

def _set(node, attr_name, value, **Kwargs):
	""" Assigns value to the given attribute
	Args : 
		value (attribute specific) : value to be assigned
	"""
	return node.setAttr(attr_name, value, Kwargs)

def _get(node, attr_name, **Kwargs):
	""" Use this to query the attributes' current value
	Return :
		(attribute specific) : current value of the given attribute
	"""
	return node.getAttr(attr_name, Kwargs)

def _lock(node, attr_name, hide=True, **Kwargs):
	""" Removes access to this attribtue
	Locks attr_name and optionally hides it from the channel box
	"""
	if not type(attr_name) is list:
		attr_name = [attr_name]
	for attr in attr_name:
		node.setAttr(attr, keyable = False, lock = True, cb = not hide)

def _unlock(node, attr_name, show=True, **Kwargs):
	""" Returns access to this attribute
	Unlocks attr_name and optionally shows it in the channel box
	"""
	if type(attr_name) is str:
		attr_name = [attr_name]
	for attr in attr_name:
		node.setAttr(attr, keyable = True, lock = False, cb = show)

#TODO should this be done in nodes.py?
def _link(node, attr_name, target_node, f=False):
	""" Connects the same attribute between two ndoes
	Assumes the same attribute is present in both nodes
	Args :  node : node that will drive the attr's value
			attr_name (str): common attribute to be linked between
			target_node : receiving node of the connection
	"""
	_connect(node, attr_name, target_node, attr_name, f=f)

def _connect(node, attr_name, target_node, target_attr, f=False):
	"""Makes a direct connection from attr_name to target_attr
	Args : 
		
	"""
	node.connectAttr(attr_name, '{}.{}'.format(target_node, target_attr), f =f)

def _connectReverse(node, attr_name, target_node, target_attr, f=False):
	""" Makes a reverse connection between attributes
	Works like _connect but it runs the source attribute through a reverse node
	"""
	rev_name = '{}_{}_REV'.format(node, attr_name)
	if not pm.objExists(rev_name):
		rev = pm.createNode('reverse', name = rev_name)
		_connect(node, attr_name, rev, 'inputX')
		rev_node = rev
	else:
		rev_node = pm.PyNode(rev_name)
	_connect(rev_node, 'outputX', target_node, target_attr, f = f)

def _connectNegative(node, attr_name, target_node, target_attr, f=False):
	""" Connect the negative value of an attribute into another
	Works like _connect but multiplies the attr_name value by -1
	"""
	mul_name = '{}_{}_neg'.format(node, attr)
	if not pm.objExists(mul_name):
		mul_node = pm.createNode('multiplyDivide', name = mul_name)
		mul_node.setAttr('input2X', -1)
		_connect(node, attr_name, mul_node, 'input1X')
	else:
		mul_node = pm.PyNode(mul_name)
	
	_connect(mul_node, 'outputX', target_node, target_attr, f = f)