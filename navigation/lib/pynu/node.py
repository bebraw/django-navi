# -*- coding: utf-8 -*-
"""
Helper classes.
"""
"""
Pynu - Python Node Utilities
Copyright (C) 2010 Juho Vepsäläinen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see http://www.gnu.org/licenses/
"""
import re


class NodeContainer(object):

    def __init__(self, owner, name, complementary_name):
        super(NodeContainer, self).__init__()

        self._nodes = list()
        self.owner = owner
        self.name = name
        self.complementary_name = complementary_name

    def __getitem__(self, key):
        return self._nodes[key]

    def __eq__(self, other):
        """Checks if container contents are equal to other.

        >>> node1, node2, node3 = Node(), Node(), Node()
        >>>
        >>> assert node1.children == None
        >>>
        >>> node1.children = node3
        >>> node2.children = node3
        >>>
        >>> assert node1.children == [node3, ]
        >>> assert node1.children == node2.children
        """
        if len(self._nodes) == 0 and other is None:
            return True

        return self._nodes == other

    def ___neq__(self, other):
        """Checks if container contents are not equal to other.

        >>> node1, node2, node3 = Node(), Node(), Node()
        >>>
        >>> node1.children = node3
        >>> node2.children = node3
        >>>
        >>> assert node1.children != [node2, ]
        >>> assert node1.children != node3.children
        """
        return not self == other

    def __len__(self):
        return len(self._nodes)

    def _set_content(self, content):
        """Sets content of the container.

        >>> node1, node2 = Node(), Node()
        >>> node1.children._set_content(node2)
        >>>
        >>> assert node1.children == [node2, ]
        >>> assert node2.parents == [node1, ]
        >>>
        >>> node3 = Node()
        >>> node1.children._set_content(node3)
        >>>
        >>> assert node1.children == [node3, ]
        >>> assert node2.parents == None
        """
        self.empty()

        if hasattr(content, '__iter__'):
            self.append(*content)
        else:
            self.append(content)

    def empty(self):
        """Empties container content.

        >>> node1, node2 = Node(), Node()
        >>>
        >>> node1.children = node2
        >>> node1.children.empty()
        >>>
        >>> assert len(node1.children) == 0
        >>> assert len(node2.parents) == 0
        """
        for item in self._nodes:
            self._nodes.remove(item)
            complementary_items = getattr(item,
                self.complementary_name)
            complementary_items.remove(self.owner)

    def append(self, *items):
        """Appends given items to container.

        Regular case

        >>> node1, node2 = Node(), Node()
        >>>
        >>> node1.children = node2
        >>>
        >>> assert node1.children[0] == node2
        >>> assert node2.parents[0] == node1

        Cycles are allowed by default

        >>> node1.parents.append(node2)
        >>>
        >>> assert node2.children[0] == node1
        >>> assert node1.parents[0] == node2

        Append multiple times

        >>> node1, node2 = Node(), Node()
        >>> node1.children.append(node2)
        >>> node1.children.append(node2)
        >>>
        >>> assert node1.children[0] == node2
        >>> assert node2.parents[0] == node1
        >>> assert len(node1.children) == 1
        >>> assert len(node2.parents) == 1

        Append multiple at once

        >>> node1, node2, node3 = Node(), Node(), Node()
        >>>
        >>> node1.children = (node2, node3)
        >>>
        >>> assert len(node1.children) == 2
        >>> assert node2 in node1.children
        >>> assert node3 in node1.children
        """
        for item in items:
            if item not in self._nodes:
                self._nodes.append(item)
                complementary_items = getattr(item,
                    self.complementary_name)
                complementary_items.append(self.owner)

    def remove(self, *items):
        """Removes given items from container.

        Regular case

        >>> node1, node2 = Node(), Node()
        >>>
        >>> node1.children = node2
        >>> node1.children.remove(node2)
        >>>
        >>> assert len(node1.children) == 0
        >>> assert len(node2.parents) == 0

        Remove multiple times

        >>> node1, node2 = Node(), Node()
        >>>
        >>> node1.parents = node2
        >>> node1.parents.remove(node2)
        >>> node1.parents.remove(node2)
        >>> node1.parents.remove(node2)
        >>>
        >>> assert len(node1.parents) == 0
        >>> assert len(node2.children) == 0

        Remove multiple at once

        >>> node1, node2, node3 = Node(), Node(), Node()
        >>>
        >>> node1.children = (node2, node3)
        >>> node1.children.remove(node2, node3)
        >>>
        >>> assert len(node1.children) == 0
        """
        for item in items:
            if item in self:
                self._nodes.remove(item)
                complementary_items = getattr(item,
                    self.complementary_name)
                complementary_items.remove(self.owner)

    def find(self, **kvargs):
        """Finds nodes matching to given rules. The idea is that the method
        seeks based on the type of the container. For example in case
        "node.parents.find" is invoked, it goes through all parents beginning
        from the parents of the given node.

        Default case

        >>> node1, node2, node3, node4 = Node(), Node(), Node(), Node()
        >>>
        >>> node1.children = (node2, node3)
        >>> node3.parents.append(node4)
        >>>
        >>> node1.name = 'joe'
        >>> node1.value = 13
        >>> node2.color = 'blue'
        >>> node3.color = 'black'
        >>> node4.value = 13

        Single argument, single result

        >>> assert node2.parents.find(name='joe') == node1
        >>> assert node1.children.find(color='blue') == node2

        Single argument, multiple results

        >>> assert node3.parents.find(value=13) == [node1, node4]

        Multiple arguments, single result

        >>> assert node2.parents.find(name='joe', value=13) == node1

        Regex argument (match anything except newline)

        >>> assert node2.parents.find(name='.') == node1

        Regex argument (match from beginning)

        >>> assert node1.children.find(color='^bl') == [node2, node3]

        No result

        >>> assert node2.parents.find(color='red') == None

        Cyclic case

        >>> node1, node2 = Node(), Node()
        >>>
        >>> node1.children = node2
        >>> node2.children = node1
        >>>
        >>> node1.name = 'joe'
        >>> node2.name = 'jack'

        Single argument, single result

        >>> assert node1.children.find(name='joe') == node1
        >>> assert node1.children.find(name='jack') == node2
        """
        found_nodes = self._recursion(kvargs, [], [])

        if len(found_nodes) > 0:
            return found_nodes[0] if len(found_nodes) == 1 else found_nodes

    def _recursion(self, search_clauses, found_nodes, visited_nodes):
        visited_nodes.append(self.owner)

        for node in self._nodes:
            try:
                if self._all_match(node, search_clauses):
                    found_nodes.append(node)
            except AttributeError:
                pass

            if node not in visited_nodes:
                node_container = getattr(node, self.name)

                node_container._recursion(search_clauses, found_nodes,
                    visited_nodes)

        return found_nodes

    def _all_match(self, node, search_clauses):
        for wanted_attribute, wanted_value in search_clauses.items():
            attribute_value = getattr(node, wanted_attribute)

            if isinstance(wanted_value, str):
                matched = re.match(wanted_value, attribute_value)
            else:
                matched = wanted_value == attribute_value

            if not matched:
                return False

        return True


class Node(object):
    _children_container = NodeContainer
    _children_name = 'children'
    _parents_container = NodeContainer
    _parents_name = 'parents'

    def __init__(self):

        def set_container(container, name, complementary_name):
            setattr(self, name, container(self, name, complementary_name))

        set_container(self._children_container, self._children_name,
            self._parents_name)
        set_container(self._parents_container, self._parents_name,
            self._children_name)

    def __setattr__(self, name, value):
        """ Assignment of children/parents resets previous content and creates
        needed links to nodes. Otherwise setting attributes works as expected.

        Simple assignment

        >>> node1, node2 = Node(), Node()
        >>> node1.children = node2
        >>>
        >>> assert node1.children[0] == node2
        >>> assert node2.parents[0] == node1

        Tuple assignment

        >>> node1, node2, node3 = Node(), Node(), Node()
        >>> node1.children = (node2, node3)
        >>>
        >>> assert node1.children[0] == node2
        >>> assert node2.parents[0] == node1
        >>> assert node1.children[1] == node3
        >>> assert node3.parents[0] == node1

        Assign value to an attribute

        >>> node = Node()
        >>>
        >>> node.value = 13
        >>> assert node.value == 13
        """

        def container_template(container_name):
            if hasattr(self, container_name):
                container = getattr(self, container_name)
                container._set_content(value)
            else:
                super(Node, self).__setattr__(name, value)

        if name in (self._children_name, self._parents_name):
            container_template(name)
        else:
            super(Node, self).__setattr__(name, value)
