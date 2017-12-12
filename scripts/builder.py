import os
import sys
import imp 
from CARF.scripts import session
from CARF.scripts.maya_core import maya_files
reload(maya_files)
class Builder(object):
	"""
	Handles the build process of a given asset, requires a session object with
	paths information. It will create a Rig object based on each asset build
	code.
	"""
	def __init__(self, session_obj):
		
		self.session_obj = session_obj
		self.build_file = '%s_build.py' % session_obj.asset_name
		
		self.rig_base = False
		#Dynamically imports and reload [asset_name]_build.py
		asset_module = imp.load_source(
			'imported_asset_module',
			os.path.join(session_obj.paths['asset'],self.build_file)
		)

		#Creates a Rig object from the imported module
		self.rig = asset_module.Asset()

	def import_geo(self):
		"""Description
		"""
		maya_files.import_file(self.session_obj.paths['geo'])

		if self.rig_base:
			#Import into rig base, once we have a rig base...
			pass
		

	def build_template(self):
		pass
	
	def build_rig(self):
		"""Runs the base level rig build and calls the asset level rig build"""

		self.rig.build_rig()