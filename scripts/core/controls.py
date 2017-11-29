#Sys imports
import json

#Maya imports
import pymel.core as pm 
import maya.cmds as cmds

#Global data import
from ACtools.data import global_data as g_data

#Modules improt
from ACtools.scripts.core import transforms as trans

reload(g_data)
reload(trans)


class Control(trans.Transform):
	"""docstring for Control"""
	def __init__(self, name, shape, color=None, size=1, side= g_data.center, 
		add_zero=True, add_space=True, parent=None, position=[0,0,0,0,0,0]):

		#Empty attributes for clarity of mind
		self.shapes = []
		self.size = size
		ctr_name = name 
		
		#CBB remove this? have it NOT allow for preffix in name?
		if not name.split('_')[-1] == '_CTR':
			ctr_name = '%s_CTR' % ctr_name

		super(Control, self).__init__(name = ctr_name, side = side, 
			add_zero = add_zero, add_space = add_space, parent = parent, 
			position = position, node_type = 'control')

		self.create_ctr_shape(shape)
		if color:
			self.set_color(color = color)
		else:
			self.set_color(color = g_data.sides_color[side])

	def create_ctr_shape(self, shape):
		""" Creates curve shape and parents it under ctr transform
		"""
		#Loads shapes dictionary
		shape_file_read = open(g_data.ctrls_shapes_file,'r')
		shapes_dictionary = json.load(shape_file_read)
		
		#Args validation
		if not shape in shapes_dictionary.keys():
			raise Exception('%s is not a registered shape')

		#Extracts data
		shapes_data = shapes_dictionary[shape]
		for curve_data in shapes_data.keys():
			curve_degree = shapes_data[curve_data]['degree']
			curve_form = shapes_data[curve_data]['form']
			
			#Points are multiplied by size
			point_data = shapes_data[curve_data]['points']
			curve_points = [p*self.size for p in point_data]
			
			#Create curve in maya
			temp_curve = pm.curve(name = self.name, degree = curve_degree, 
				point = curve_points)
			if curve_form == 2: #2 is closed
				pm.closeCurve(temp_curve, preserveShape = False, 
					replaceOriginal = True)
			
			curve_shape = temp_curve.getShape()
			#Parent curve shape under control and delete temp transform
			pm.parent(curve_shape, self.pm_node, r = 1, s = 1)
			pm.delete(temp_curve)
			
			#Store shape in object attribute
			self.shapes.append(curve_shape)
	
	def set_color(self, color):
		"""Description
		Args:
			color (str) : if passed as a string, it can be one of the following
				options: 'blue', 'red', 'yellow', 'green', 'pink'. 
				Prefixes available for the options: 'light_' and 'dark_'
				Examples: 'dark_red', 'light_green', 'pink'
			color (int) : if passed as an int, it represents the index value of
				the Color attribute in the Drawing override tab for Maya
		"""
		
		if type(color) is int:
			color_index = color
		elif type(color) is str:
			color_index = g_data.colors_dict[color]
		else:
			raise Exception('Color should be an integer or a string')
		
		for shape in self.shapes:
			cmds.setAttr('%s.overrideEnabled' % shape, 1)
			cmds.setAttr('%s.overrideColor' % shape, color_index)
	
	
def get_curve_data(shape):
	"""Gets shape's degree and point information
	Returns the name of the curve, degree and point positio (In that order)
	"""
	
	curve_degree = cmds.getAttr('%s.degree' % shape)
	curve_spans = cmds.getAttr('%s.spans' % shape)
	curve_form = cmds.getAttr('%s.form' % shape)
	
	points = curve_degree + curve_spans

	if curve_form == 2:
		points = curve_spans
	curve_points = []
	for i in range(points):
		curve_points.append(cmds.pointPosition('%s.cv[%i]' % (shape, i), l = 1))
	
	curve_data = [curve_degree, curve_form, curve_points]

	return curve_data

def export_ctrl_shape(ctr_name):

	name = ctr_name.replace('_CTR','')
	entries = {}

	data_dict = {
		name:entries
	}
	
	for x,shape in enumerate(cmds.listRelatives(ctr_name, shapes = 1)):
		shape_data = get_curve_data(shape)
		entries['shape%i' % x] = {
			'degree':shape_data[0],
			'form':shape_data[1],
			'points':shape_data[2]
		}
	return data_dict


def add_to_controls_shape(ctr_name):
	""" Adds control to control shape file
	"""
	#get data
	# data = get_curve_data(control)
	ctr_dictionary = export_ctrl_shape(ctr_name)

	#Open Json file and Merge dictionaries
	shape_file_read = open(g_data.ctrls_shapes_file,'r')
	current_shapes = json.load(shape_file_read)
	current_shapes.update(ctr_dictionary)

	j_data = current_shapes.copy()
	shape_file_read.close()
	
	#Save new json file
	shape_file_write = open(g_data.ctrls_shapes_file,'w')

	json.dump(
		j_data, 
		shape_file_write,
		indent = 4,
		sort_keys = True
	)

	shape_file_write.close()