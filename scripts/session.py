#Sys imports
import os
import shutil

#Module imports
from ACtools.scripts.maya_core import maya_files

#Global data import
from ACtools.data import global_data as g_data
reload(g_data)
class Session(object):
	"""
	Session class.
	Handles the directory information needed for each asset, opening of files
	and publishing.
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
		self.asset_set = False
		self.asset_name = None
		self.asset_built = False
		
		if project_name:
			self.set_project()
		#If asset_name is provided, set the data
		if asset_name  and asset_type:
			self.set_asset(asset_name, asset_type)

	def set_project(self, project_name):

		if not project_name in Session.existing_projects:
			raise Exception('%s is not an existing project, unable to set data'\
			'. Please use create_project() to add a new project' % project_name)
		
		self.project_name = project_name
		self.project_path = os.path.join(g_data.productions_root, project_name)

		###Hard coded for now, names come from g_data.project_folders
		self.paths['checkin'] = os.path.join(self.project_path, 
														'Checkins', 'Assets')
		self.paths['final'] = os.path.join(self.project_path,
														'Final', 'Assets')

		#List of all assets under current project
		self.project_assets = os.listdir(self.project_path)

		self.project_set = True
	
	def create_set_project(self, project_name):
		self.create_project(project_name)
		self.set_project(project_name)

	def create_project(self, project_name):
		""" Creates the folder structure for a new project
		Args:
			project_name (str) : Name to be used for the project.
		"""
		
		project_path = os.path.join(g_data.productions_root, project_name)
		if os.path.isdir(project_path):
			print '##Warning: %s already exists as a project,'\
			' no folders created' % project_name
		else:
			create_folder(project_path)

		self.create_directory_tree(project_path, g_data.project_folders)

		Session.existing_projects.append(project_name)

	def create_directory_tree(self,base_path, folders_dictionary):
		"""Recursive method, it will create a directory tree in the given path
		based on the given dictionary
		Args:
			base_path (os path) : path where to start creating directories
			folders_dictionary (dict) : Dictionary representing the directory
				tree. Check global_data.py for more info on folders dictionaries
		"""
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
			#Set geo path
			self.paths['geo'] = os.path.join(self.paths['final'], asset_type, 
				asset_name, '%s_geo.ma' % asset_name)
			#Setting the asset data
			self.asset_name = asset_name
			self.asset_type = asset_type
			asset_path = os.path.join(self.user_path, asset_name)

			#Check for asset folder
			create_folder(asset_path)
			self.create_directory_tree(asset_path, g_data.asset_dev_folders)
			
			self.paths['asset'] = asset_path
			#Add asset dev folders to paths
			for folder in g_data.asset_dev_folders:
				f_path = os.path.join(self.paths['asset'], folder)
				self.paths[folder] = f_path
			
			#Check for asset_build.py
			build_path = os.path.join(asset_path, 
				'%s_build.py' % self.asset_name)
			if not os.path.isfile(build_path):
				self.create_build_file(build_path, asset_type)

			self.asset_set = True
		
	def check_in_asset(self):
		"""Saves the current asset dev folders into the checkins directory.
		Checks for older versions in Checkins. If found, creates a new one to 
		save the new data. 
		Versions are numbers with padding of 3
		"""
		if not self.asset_set:
			raise Exception('Asset data not set. Unable to check-in the data')
		
		#Check and creates Chekins directory
		checkin_path = os.path.join(self.paths['checkin'], self.asset_type,
			self.asset_name)
		create_folder(checkin_path)

		#Get the next version number			
		versions = [int(x) for x in os.listdir(checkin_path)]
		new_version = 0 if versions == [] else max(versions)+1
		version_path = os.path.join(checkin_path, str(new_version).zfill(3))

		#Copies the asset development folders into the new version checkin
		shutil.copytree(self.paths['asset'], version_path)

	def publish_asset(self):
		"""Description
		"""
		# if not self.asset_built:
		# 	raise Exception('Asset was not succesfully built. Please build'\
		# 		'succesfully and try again')
		
		#Check and creates the asset directory in the final drive
		final_path = os.path.join(self.paths['final'], self.asset_type,
			self.asset_name)
		create_folder(final_path)

		rig_path = os.path.join(final_path, 'Rig')
		create_folder(rig_path)			
		
		archive_path = os.path.join(rig_path,'Archive')
		create_folder(archive_path)

		#Get the next version number			
		versions = [int(x) for x in os.listdir(archive_path)]
		new_version = 0 if versions == [] else max(versions)+1
		version_path = os.path.join(archive_path, str(new_version).zfill(3))
		create_folder(version_path)

		for folder_path in [rig_path, version_path]:
			file_path = os.path.join(folder_path,'%s_rig.ma' % self.asset_name)
			maya_files.save_file_as(file_path)
		
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