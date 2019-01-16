# Sys imports
import os
import shutil

# Module imports
from CARF.scripts.maya_core import maya_files

# Global data import
from CARF.data import global_data as g_data

# Global constants
__fixed_paths__ = {
	'tools_scripts': os.path.dirname(__file__),
	'source_build': os.path.join(os.path.dirname(__file__),'asset_build.py'),
	'components': os.path.join(os.path.dirname(__file__),'components')
}
__existing_projects__ = os.listdir(g_data.productions_root)

class Session(object):
	"""
	Session class.
	Handles the directory information needed for each asset, opening of files
	and publishing.
	"""
	def __init__(self, user, project_name = None, asset_name=None, 
			asset_type = None, rig_type = None):
		"""
		Args:
			param1 (type) : Description
		"""
		
		self.user_name = user
		self.user_path = os.path.join(g_data.users_root, self.user_name)
		self.paths = dict(__fixed_paths__)

		# Set up backups directory
		self.user_backups_path = os.path.join(self.user_path, 
											  '__assets_backups__')
		if not os.path.isdir(self.user_backups_path):
			check_create_folder(self.user_backups_path)

		#Empty attributes for clarity of mind
		self.project_name = None
		self.project_path = None
		self.project_set = False

		#Asset related attributes
		self.asset_name = None
		self.asset_set = False
		self.asset_directory_created = False

		if project_name:
			self.set_project()
		#If asset_name is provided, set the data
		if asset_name and asset_type and rig_type:
			self.set_asset(asset_name, asset_type, rig_type)

	def set_project(self, project_name):

		if not project_name in __existing_projects__:
			raise Exception(
				'{} is not an existing project: unable to set data.\n'\
				'Please use create_project() to add a new project'\
				.format(project_name)
			)
		
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
			check_create_folder(project_path)

		self.create_directory_tree(project_path, g_data.project_folders)

		__existing_projects__.append(project_name)

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
			check_create_folder(folder_path)
			if folders_dictionary[folder]:
				self.create_directory_tree(folder_path, 
					folders_dictionary[folder])

	def set_asset(self, asset_name, asset_type, rig_type):
		""" Changes the current session asset. 
		This implies updating all the 'paths' for this session. It checks
		whether or not this paths are valid by checking if the asset directory
		exists
		"""
		if not self.project_set :
			raise Exception('Project data not found. Please set project'\
							' before setting the asset')

		#Validation of arguments
		if not (type(asset_name) is str or type (asset_type) is str):
			raise Exception("Asset name and type should be a string")
		
		elif rig_type not in g_data.supported_rig_types:
			raise Exception(
				'%s is not an supported rig type. Supported '\
				'types are: %s' % (rig_type, g_data.supported_rig_types)
			)
		
		#Updating the asset name and type
		self.asset_name = asset_name
		self.asset_type = asset_type
		
		asset_path = os.path.join(self.user_path, asset_name)
		
		if not os.path.exists(asset_path):
			self.asset_directory_created = False
			
		self.paths['asset'] = asset_path
		
		#Set geo path
		self.paths['geo'] = os.path.join(
			self.paths['final'], asset_type, 
			asset_name, 'Geo', '%s.ma' % asset_name
		)

		#Add asset dev folders to paths
		for folder in g_data.asset_dev_folders:
			f_path = os.path.join(self.paths['asset'], folder)
			self.paths[folder] = f_path
		
		build_path = os.path.join(asset_path, '%s_build.py' % self.asset_name)
		self.paths['build'] = build_path
		
		self.asset_set = True
	
	def create_asset_workspace(self):
		""" Creates the working directories for the current assets
		It will create the asset_dev_folders directory tree found in 
		global_data.py and it will create the asset_build.py file
		"""
		#Check for asset folder
		check_create_folder(asset_path)
		self.create_directory_tree(asset_path, g_data.asset_dev_folders)
		
		#Check for asset_build.py
		build_path = os.path.join(asset_path, '%s_build.py' % self.asset_name)
		if not os.path.isfile(build_path):
			self.create_build_file(build_path, rig_type)
		
		self.asset_directory_created = True
		
		
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
		check_create_folder(checkin_path)

		#Get the next version number			
		versions = [int(x) for x in os.listdir(checkin_path)]
		new_version = 0 if versions == [] else max(versions)+1
		version_path = os.path.join(checkin_path, str(new_version).zfill(3))

		#Copies the asset development folders into the new version checkin
		shutil.copytree(self.paths['asset'], version_path)
	
	def check_out_asset(self):
		""" Looks for the latest asset directory in the Checkins folder, then
		makes a local copy into the current's user Asset Dev

		If There is an existing asset directory in the users dev area, then it
		moves the current directory into the Stash folder, then checks out the
		latest asset directory
		"""
		if not self.asset_set:
			raise Exception('Asset data not set. Unable to check-out the data')
		
		#Gathering the latest checked data
		checkin_path = os.path.join(self.paths['checkin'], self.asset_type,
			self.asset_name)
		
		if not os.path.isdir(checkin_path):
			raise Exception(
				'Unable to check out data: '\
				'No checked in data found for {}'.format(self.asset_name)
			)
		if not len(os.listdir(checkin_path)):
			raise Exception(
				'Unable to check out data: '\
				'Check in directory for {} is empty, no data to copy from'\
				.format(self.asset_name)
			)
		
		versions = [int(x) for x in os.listdir(checkin_path)]
		latest_version = max(versions)
		latest_checked_data = os.path.join(checkin_path, 
										   str(latest_version).zfill(3))
		#User Asset dev
		user_asset_path = self.paths['asset']

		# If user data is present, back it up and then remove it
		if os.path.isdir(user_asset_path):
			self.backup_user_asset_data()
			shutil.rmtree(user_asset_path)
		
		#Copies from latest into user dev folder
		shutil.copytree(latest_checked_data, user_asset_path)

	def backup_user_asset_data(self):
		""" Makes a copy of the user's current asset data in the 
		__assets_backups__ folder

		It saves each new backup with a bigger increment suffix. 
		TODO: implement the following... 
		if the amount of backups is the same as the maximum number of backups 
		specified in global_data, delete the oldest
		"""
		#Look for the next backup increment and use it as the directory name
		next_backup = len(os.listdir(self.user_backups_path)) + 1
		backup_name = '_'.join([self.asset_name, str(next_backup).zfill(3)])
		backup_path = os.path.join(self.user_backups_path, backup_name)

		#Create the backup
		user_asset_path = self.paths['asset']
		shutil.copytree(user_asset_path, backup_path)

	def publish_asset(self):
		"""Checks in the asset, then saves the current maya file into the
		publish folder. 
		
		If there is an existing publish, it will add it to the archive as an
		increment.
		"""
		
		self.check_in_asset()

		#Check and creates the asset directory in the final drive
		final_path = os.path.join(self.paths['final'], self.asset_type,
								  self.asset_name)
		check_create_folder(final_path)

		rig_path = os.path.join(final_path, 'Rig')
		check_create_folder(rig_path)			
		
		archive_path = os.path.join(rig_path,'Archive')
		check_create_folder(archive_path)

		#Get the next version number			
		versions = [int(x) for x in os.listdir(archive_path)]
		new_version = 0 if versions == [] else max(versions)+1
		version_path = os.path.join(archive_path, str(new_version).zfill(3))
		check_create_folder(version_path)

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

def check_create_folder(folder_path):
	"""Checks for existing folder, if not found, creates it """
	if not os.path.exists(folder_path):
		os.mkdir(folder_path)