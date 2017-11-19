#Sys imports
import os
import shutil

#Global data import
from ACtools.data import global_data as g_data

class Session(object):
	"""
	Session class.
	Handles the directory information needed for each asset, opening of files
	and publishing.

	temp root = D:\Productions

	"""
	fixed_paths = {
		'tools_scripts': os.path.dirname(__file__),
		'source_build': os.path.join(os.path.dirname(__file__),'asset_build.py'),
		'components': os.path.join(os.path.dirname(__file__),'components')
	}

	dev_folders = ['template','weights','wip','geo','scenes']
	def __init__(self, project_name, asset_name=None, asset_type = None):
		
		
		
		self.project_name = project_name

		#Creates project folder if needed
		self.project_path = os.path.join(g_data.sys_root, project_name)
		create_folder(self.project_path)

		#Asset related attributes
		self.asset_bool = False
		self.asset_name = asset_name
		self.paths = dict(Session.fixed_paths)

		#List of all assets under current project
		self.project_assets = os.listdir(self.project_path)
		

		#If asset_name is provided, set the data
		if asset_name != None and asset_type != None:
			self.set_asset(asset_name, asset_type)
	

	def set_asset(self, asset_name, asset_type):
		"""
		Creates all the required folders for an asset build, sets the data
		"""
		#Validation of arguments
		if not (type(asset_name) is str or type (asset_type) is str):
			raise Exception("Asset name and type should be a string")
		elif asset_type not in g_data.supported_asset_types:
			raise Exception('%s is not an supported asset type supported types'\
			' are: %s' % (asset_type, g_data.supported_asset_types))
		else:
			#Setting the asset data
			self.asset_name = asset_name
			asset_path = os.path.join(self.project_path, asset_name)

			#Check for asset folder
			if not self.asset_name in self.project_assets:
				os.mkdir(asset_path)
				self.project_assets.append(self.asset_name)
			
			self.paths['asset'] = asset_path
			self.asset_bool = True
			
			#Check for needed folders
			for f in Session.dev_folders:
				f_path = os.path.join(self.paths['asset'], f)
				create_folder(f_path)
				self.paths[f]	 = f_path
			
			#Check for asset_build.py
			build_path = os.path.join(asset_path, 
				'%s_build.py' % self.asset_name)

			if not os.path.isfile(build_path):
				self.create_build_file(build_path, asset_type)
		

	def open_build(self):
		open_in_os(self.paths['build'])

	def open_asset_directory(self):
		open_in_os(self.paths['asset'])

	def create_build_file(self, build_path, asset_type):
		'''Creates a copy of asset_build.py  in the dev folder
		args:
			build_path (str) : Path to build file in dev folder
			asset_type (str) : Rig type name
		'''

		source_build = self.paths['source_build']
		temp_path = build_path.replace('build','temp')

		shutil.copy(source_build, build_path) #Copy build

		shutil.copy(source_build, temp_path) #Temp file to replace

		asset_build = open(build_path, 'w+')
		temp_build = open(temp_path, 'r')

		#rewritting asset_build with values instead of tokens
		replace_tokens = {
			'asset_token':self.asset_name,
			'type_token':asset_type,
			'Type_token':asset_type.capitalize(),
		}
		for l in temp_build:
			for tok in replace_tokens.keys():
				if tok in l:
					l = l.replace(tok, replace_tokens[tok])
			asset_build.write(l)
		
		#Close files and remove temp
		asset_build.close()
		temp_build.close()
		os.remove(temp_path)

		
		self.paths['build'] = build_path

def open_in_os(path):
	""" Relative to each OS, opens given path """
	os.startfile(path)

def create_folder(folder_path):
	"""Checks for existing folder, if not found, creates it """
	if not os.path.exists(folder_path):
		os.mkdir(folder_path)