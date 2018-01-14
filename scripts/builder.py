#Python imports
import os
import sys
import imp 

#Maya imports
import pymel.core as pm

#CARF imports
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
		self.asset_module = imp.load_source(
			'imported_asset_module',
			os.path.join(session_obj.paths['asset'],self.build_file)
		)

	def initialize_rig(self):
		""" Creates an instance of the rig object
		"""
		#Creates a Rig object from the imported module
		self.rig = self.asset_module.Asset(
			builder = self,
			asset_name = self.session_obj.asset_name
		)

	def setup_rig_base(self):
		""" Builds base groups and root controller. 
		Sets rig_base attribute
		"""
		self.rig.build_base()
		self.rig_base = True


	def import_geo(self):
		"""Imports the asset geo to the scene. 
		If there's a rig base, it parents the imported geo under GEO_GRP
		TODO : 
			So far this is the only method using maya calls, even if the geo has
			a top group with a required name (like the asset name) this will
			still require onm maya call to "parent" that group. In the meantime
			it looks for the top transform and parents that, using maya calls
		"""
		new_nodes = maya_files.import_file(self.session_obj.paths['geo'])

		if self.rig_base:
			#Looks for top transform that should be grouping all the geometry
			transform_nodes = pm.ls(new_nodes, et = 'transform')
			top_grp = None
			
			for grp in transform_nodes:
				if not grp.getParent():
					top_grp = grp
			
			#Setting the parent
			top_grp.setParent('GEO_GRP') 
		
		return new_nodes
		

	def build_template(self):
		pass
	
	def assemble_rig(self):
		""" Wrapper for the rig build method.
		Builds all components and then executes the asset's build code
		"""
		self.rig.build()
		pass
	
	def build_rig(self):
		"""Builds the final rig.
		This will create a new scene and a new instance of the rig object. Don't
		use this if building step by step.
		Executed steps:
			Makes a new scene
			Creates base groups
			Imports geos
			Assembles all the rig components
			Binds geometry
			Finalizes the rig
		"""
		maya_files.new_file() #New scene
		
		self.initialize_rig() #Instanciates rig object

		self.setup_rig_base() #Creates base groups and root

		self.import_geo() #Imports the geo and parents it under the rig

		self.assemble_rig() #Builds all the components for the rig