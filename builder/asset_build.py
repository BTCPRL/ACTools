"""
asset_token build
"""
import pymel.core as pm 
import maya.cmds as cmds

from CARF.scripts.maya_core import nodes, transforms
from CARF.scripts.rigs import type_token

reload(type_token)
class Asset(type_token.Type_token):
	
	def __init__(self,  asset_name):
		""" Declare custom attributes here
		It is not recommended adding logic here, just declare what will be used
		later in the different steps of the build process
		"""
		super(Asset, self).__init__(asset_name)

	def configure_rig(self,  asset_name):
		""" Change the default behavior for the rig or the components
		Changes made here will effect how components get build
		"""
		super(Asset, self).configure_rig()

	def build(self):
		""" All components get built here, add or remove functionallity
		according to your needs
		"""
		super(Asset, self).build()
