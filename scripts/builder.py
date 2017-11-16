import os
import sys
import imp 
from ACtools.scripts import session

class Builder(object):
	"""
	Handles the build process of a given asset, requires a session object with
	paths information. It will create a Rig object based on each asset build
	code.
	"""
	def __init__(self, session_obj):
		
		self.session_obj = session_obj

		self.build_file = '%s_build.py' % session_obj.asset_name
		
		#Dynamically imports and reload [asset_name]_build.py
		asset_module = imp.load_source(
			'imported_asset_module',
			os.path.join(session_obj.asset_paths['asset'],self.build_file)
		)

		#Creates a Rig object from the imported module
		self.rig = asset_module.Asset()


	def build_template(self):
		pass
	
	def build_rig(self):
		"""Runs the base level rig build and calls the asset level rig build"""

		self.rig.build_rig()