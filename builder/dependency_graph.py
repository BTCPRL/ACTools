def travel_graph(function):
    """Decorator that applies function to each node in the graph, following the
    dependency order
    Args:
        function (function) : function to be run for each node
    Returns:
        function: wrapped function
    """
    def decorator_wrapper(obj_instance, start, **kwargs):
        """Catches the argument for the function
        Args:
            start (Graph_node): first node of the graph
            **kwargs :  arguments to pass to the function
        """
        function(obj_instance, start, **kwargs)
        for node in start.children:
            decorator_wrapper(obj_instance, start=node, **kwargs)
    return decorator_wrapper


class Graph_node(object):
    """Nodes that populate a dependency graph
    """

    def __init__(self, name, parent=None):

        self.name = name
        self.parent = parent
        self.children = []

    def __repr__(self):
        return self.name

    def link_parent(self, parent_node):
        """ Creates a parent-child relationship between nodes
        Args:
            parent_node (Graph_node) : Graph node to set as parent
        """
        self.parent = parent_node
        parent_node.children.append(self)

    def link_child(self, child_node):
        """ Creates a connection from this node to the child_node
        Args:
            child_node (Graph_node) : Graph node to set as child
        """
        self.children.append(child_node)
        child_node.parent = self


class Dependency_graph(object):
    """ Graph to track a sequence of dependencies
    """

    def __init__(self, graph_name, graph_root_name=None):

        self.graph_name = graph_name
        self.nodes = {}
        self.root_node = None
        if graph_root_name:
            self.root_node = Graph_node(graph_root_name)
            self.nodes[graph_root_name] = self.root_node

    def add_node(self, node_name, node_parent):
        """ Inserts a node into the graph's dependencies
        Args:
            node_name (str) : Node's name
            node_parent (str) : Node parent's name
        """
        # Validations
        if node_name == node_parent:
            raise Exception('node name needs to be different thant parent')

        if not self.root_node:
            # If no root, new node becomes the root
            # in this case, parent will refer to sometehing outside the graph
            self.root_node = Graph_node(node_name, node_parent)

        else:
            if self.get_node(node_name, self.root_node):
                raise Exception('%s is already added to the %s graph'
                                % (node_name, self.graph_name))

            # Looking for parent
            n_parent = self.get_node(node_name=node_parent,
                                     first_node=self.root_node)
            if not n_parent:
                raise Exception('%s is not a valid parent as it is '
                                'not part of the graph' % node_parent)

            # Adding node
            new_node = Graph_node(node_name, n_parent)
            self.nodes[new_node.name] = new_node
            # Setting new node as child of it's parent
            n_parent.link_child(new_node)

    def get_node(self, node_name, first_node):
        """ Travels the graph looking for the node and returns it
        Returns:
            (Graph_node) the node found
            (bool) False if nothing was found
        """
        current_node = first_node
        found = False
        if node_name == current_node.name:
            return current_node
        else:
            for child in current_node.children:
                found = self.get_node(node_name, child)
                if found:
                    break
        return found

    def print_graph(self, start, space=''):
        print space + str(start)
        for c in start.children:
            self.print_graph(start=c,  space=space + '    ')
