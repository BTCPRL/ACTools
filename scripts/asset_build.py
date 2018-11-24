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
		super(Asset, self).__init__(asset_name)

	def build(self):
		super(Asset, self).build()
		print "build section of asset level"