#Sys imports
import os
import shutil

#Global data import
from ACtools.data import global_data as g_data
reload(g_data)
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

	dev_folders = ['template','weights','wip','scenes']
	existing_projects = os.listdir(g_data.productions_root)
	def __init__(self, user, project_name = None, asset_name=None, 
			asset_type = None):
		"""
		Args:
			param1 (type) : Description
		"""
		
		self.user_name = user
		self.user_path = os.path.join(g_data.users_root, self.user_name)
		self.paths = dict(Session.fixed_paths)
		
		#Empty attributes for clarity of mind
		self.project_name = None
		self.project_path = None
		self.project_set = False
		#Asset related attributes
		self.asset_name = None
		
		if project_name:
			self.set_project()
		#If asset_name is provided, set the data
		if asset_name  and asset_type:
			self.set_asset(asset_name, asset_type)
	
	def set_project(self, project_name):

		if not project_name in Session.existing_projects:
			raise Exception('%s is not an existing project, unable to set data'\
			'. Please use create_project() to add a new project')
		
		self.project_name = project_name
		self.project_path = os.path.join(g_data.productions_root, project_name)
		
		#List of all assets under current project
		self.project_assets = os.listdir(self.project_path)

		self.project_set = True
	
	def create_set_project(self, project_name):
		self.create_project(project_name)
		self.set_project(project_name)

	def create_project(self, project_name):
		"""
		Args:
			param1 (type) : Description
		Returns:
			type: Description 
		"""
		
		project_path = os.path.join(g_data.productions_root, project_name)
		if os.path.isdir(project_path):
			print '##Warning: %s already exists as a project,'\
			' no folders created' % project_name
		else:
			create_folder(project_path)

		self.create_directory_tree(project_path, g_data.project_folders)

	def create_directory_tree(self,base_path, folders_dictionary):
		for folder in folders_dictionary:
			folder_path = os.path.join(base_path, folder)
			create_folder(folder_path)
			if folders_dictionary[folder]:
				self.create_directory_tree(folder_path, 
					folders_dictionary[folder])
		

	def set_asset(self, asset_name, asset_type):
		"""Creates all the required folders for an asset build
		"""
		if not self.project_set :
			raise Exception('Project data not found. Please set project before'\
			' setting the asset')

		#Validation of arguments
		if not (type(asset_name) is str or type (asset_type) is str):
			raise Exception("Asset name and type should be a string")
		elif asset_type not in g_data.supported_asset_types:
			raise Exception('%s is not an supported asset type. Supported '\
			'types are: %s' % (asset_type, g_data.supported_asset_types))
		else:
			#Setting the asset data
			self.asset_name = asset_name
			asset_path = os.path.join(self.user_path, asset_name)
			self.paths['asset'] = asset_path

			#Check for asset folder
			if not self.asset_name in self.project_assets:
				create_folder(asset_path)
				self.project_assets.append(self.asset_name)
				self.create_directory_tree(asset_path, g_data.asset_dev_folders)

			#Add asset dev folders to paths
			for f in g_data.asset_dev_folders:
				f_path = os.path.join(self.paths['asset'], f)
				self.paths[f] = f_path
			
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