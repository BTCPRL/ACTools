import pymel.core as pm
import maya.cmds as cmds
from CARF import nodes

class Attribute(object):
	"""docstring for Attribute"""
	def __init__(self, attr_name, attr_type, default_value=None, min=None, 
		max=None, hidden=False, keyable=True, **Kwargs):

		#Store values		
		self.name = attr_name
		self.type = attr_type
		self.default_value = default_value
		self.min_val = min
		self.max_val = max
		self.hidden = hidden
		self.keyable = keyable
		self.lock = False

		#Adds it to the node
		args = {
			'hidden':self.hidden,
			'keyable':self.keyable,
		}
		if self.default_value != None:
			args['dv'] = self.default_value

		if self.min_val != None:
			args['min'] = self.min_val
			args['hasMaxValue'] = True

		if self.max_val != None:
			args['max'] = self.max_val
			args['hasMinValue'] = True

		self.pmNode.addAttr(self.name, at = self.type, **args)


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
	