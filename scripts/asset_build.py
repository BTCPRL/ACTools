"""
asset_token build
"""
import pymel.core as pm 
import maya.cmds as cmds

from ACtools import nodes, transforms, type_token

reload(type_token)
class Asset(type_token.Type_token):
	
	def __init__(self):
		super(Asset, self).__init__()

	def register(self, component):
		super(Asset, self).register()

	def build_template(self):
		super(Asset, self).build_template()

	def build_rig(self):
		super(Asset, self).build_rig()
		print "build section of asset level"