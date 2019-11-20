import maya.cmds as cmds
import pymel.core as pm
from CARF.data import global_data as g_data
from CARF.maya_core import attributes


class Node(object):
    """
    Nodes class.

    Creates Node objects, storing the created pymel object
    """

    """Supported types dictionary
    Format: {name: [suffix, maya type]}
    """
    _known_types_ = {
        # Utility nodes
        'condition': ['_COND', 'condition'],
        'remapValue': ['_RMV', 'remapValue', ],
        'clamp': ['_CLP', 'clamp'],
        'reverse': ['_REV', 'reverse'],
        # Basic Math
        'multiply': ['_MUL', 'multiplyDivide'],
        'divide': ['_DIV', 'multiplyDivide'],
        'add': ['_ADD', 'plusMinusAverage'],
        'substract': ['_SUB', 'plusMinusAverage'],
        # Matrices
        'decomposeMatrix': ['_DMX', 'decomposeMatrix'],
        # Curve nodes
        'nearestPointOnCurve': ['_NPC', 'nearestPointOnCurve'],
        'pointOnCurveInfo': ['_POC', 'pointOnCurveInfo'],
        # Dag nodes, they get the suffix from name
        'transform': [None, 'transform'],
        'control': [None, 'transform'],  # Used by controls module
        'joint': [None, 'joint'],
    }
    # Auto detect nodes
    _auto_detect_ = {
        'divide': 2,
        'substract': 2
    }

    @property
    def name(self):
        """ Full name of the node
        full name is of form {side}_{description}_{suffix}
        """
        return self._full_name

    @name.setter
    def name(self, name):
        """ Setter for full name attribute. 
        :arg:
        name (str): Full name of node, it should include side prefix
        """
        if len(name.split('_')) < 2:
            raise Exception('Node name should include a side prefix')

        prefix = name.split('_')[0]

        if prefix not in g_data.positions_prefifx:
            raise Exception('{} has an invalid side prefix'.format(name))

        self._full_name = name

    @property
    def node(self):
        """ This will carry the pymel node
        The Pymel node is not commonly used but kept for ease of access
        """
        return self._pm_node

    @node.setter
    def node(self, node_type):
        """ Assigns the node, if the given node_type is a list, it will assign
        the first item
        """
        if type(node_type) is list:
            self._pm_node = node_type[0]
        else:
            self._pm_node = node_type

    def __init__(self, name, node_type):
        """ Instanciates the Class and creates the maya node
        If the given node_type is supported as an auto-detect node. It will 
        set the default attributes

        :args:
        node_type (str): Which Maya node to create.
        name (str): Name to give the newly created node

        :returns:
        (Node) the instanciated object, that shares the name with the maya node
        """

        # Node base attributes
        self._full_name = None
        self._pm_node = None

        # Extract data from _known_types_ dictionary if possible
        suffix = ''
        maya_type = node_type
        if node_type in Node._known_types_.keys():
            suffix = Node._known_types_[node_type][0]
            maya_type = Node._known_types_[node_type][1]

        # Format node name
        node_name = '{}{}'.format(name, suffix)

        if cmds.objExists(node_name):
            del(self)
            raise RuntimeError("{} Already exists. Can't create it again")

        self.name = node_name

        # Create node
        node = pm.createNode(maya_type, n=self._full_name)

        if maya_type in Node._auto_detect_:
            attributes._set(node, 'operation', Node._auto_detect_[maya_type])

        self.node = node

    def __str__(self):
        return self.name

    """
	Attribute methods
		For more documentation and Args explanation, check attributes.py
	"""

    def attr_add(self, attr_name='', attr_type='slider', default_value=0,
                 min_value=None, max_value=None, hidden=False,
                 keyable=True, **Kwargs):
        """ Creates a new attribute """
        attributes._add(self._pm_node, attr_name, attr_type, default_value,
                        min_value, max_value, hidden, keyable, **Kwargs)

    def attr_get(self, attr_name, **Kwargs):
        """Returns the attribute value"""
        return attributes._get(self._pm_node, attr_name, **Kwargs)

    def attr_set(self, attr_name, value=None, **Kwargs):
        """Sets the specified value in the given attribute"""
        attributes._set(self._pm_node, attr_name, value, **Kwargs)

    def attr_lock(self, attr_name, hide=True):
        """Locks the attribute"""
        attributes._lock(self._pm_node, attr_name, hide)

    def attr_unlock(self, attr_name, show=True):
        """Unlocks the attribute"""
        attributes._lock(self._pm_node, attr_name, show, **Kwargs)

    def attr_connect(self, attr_name, target, target_attr, f=False):
        """Connects given attribute with target"""
        attributes._connect(self._pm_node, attr_name,
                            target, target_attr, f=f)

    def attr_link(self, attr_name, target, f=False):
        """Links same attribute betwen targets"""
        attributes._link(self._pm_node, attr_name, target, f=f)

    def attr_connectReverse(self, attr_name, target, target_attr, f=False):
        """Connects given attribute with target via reverse node"""
        attributes._connectReverse(self._pm_node, attr_name,
                                   target, target_attr, f=f)

    def attr_connectNegative(self, attr_name, target, target_attr, f=False):
        """Connects the negative value of the given attribute with target"""
        attributes._connectNegative(self._pm_node, attr_name,
                                    target, target_attr, f=f)
