# -*- coding: utf-8 -*-
"""
Tests for navigation.
"""
"""
Copyright (c) 2008, Heikki Heikkinen, Mikko Tyrväinen, Juho Vepsäläinen and 
Tuomas Vihinen. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the <organization> nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY <copyright holder> ``AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <copyright holder> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from django.conf.urls.defaults import patterns
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from unittest import TestCase
from amob.navigation.structure import check_node, get_navigation_root, Node
from amob.navigation.structure import TABS, get_tabs, get_user_control
from amob.navigation.urls import add_paths_to_urlpatterns
from amob.navigation.templatetags.navigationtags import contains_commands
from amob.navigation.templatetags.navigationtags import get_tree_depth
from amob.navigation.templatetags.navigationtags import render_node
#from amob.settings import STRUCTURE_PATH
#from amob.utils.yaml_reader import read_yaml

# XXX: docstring
# move to utils
def get_request(path, method):
    '''
    @param path
    @param method
    @return:
    '''
    env = {'PATH_INFO': path, 'REQUEST_METHOD': method}
    request = WSGIRequest(env)
    request.session = {}
    request.user = User()
    request.user.id = 1
    
    return request

class NodeTestCase(TestCase):
    '''
    These tests go through node functionality provided by structure.
    '''
    def setUp(self):
        '''
        Set up a simple node tree to use in testing.
        '''
        self.node1 = Node('test1')
        self.node11 = Node('command11')
        self.node2 = Node('test2')
        self.node21 = Node('test21')
        self.node22 = Node('test22')
        self.node23 = Node('test23')
        self.node221 = Node('command221')
        self.node222 = Node('command222')
        self.node231 = Node('command231')
        self.node232 = Node('command232')
        
        self.node1.next = self.node2
        self.node2.prev = self.node1
        
        self.node1.child = self.node11
        self.node11.parent = self.node1
        
        self.node2.child = self.node21
        self.node21.parent = self.node2
        
        self.node21.next = self.node22
        self.node22.prev = self.node21
        
        self.node22.next = self.node23
        self.node23.prev = self.node22
        
        self.node22.child = self.node221
        self.node221.parent = self.node22
        
        self.node221.next = self.node222
        self.node222.prev = self.node221
        
        self.node23.child = self.node231
        self.node231.parent = self.node23
        
        self.node231.next = self.node232
        self.node232.prev = self.node231

    def testName(self):
        '''
        Test to see if name of a node matches as it should.
        '''
        self.assertEquals(self.node1.name, 'test1')
        self.node1.name = 'giraffe'
        self.assertEquals(self.node1.name, 'giraffe')
    
    def testItemAdd(self):
        '''
        Test to see if adding an item works.
        '''
        items = ['test1', 'cat']
        self.node1.next = Node('cat')
        i = 0
        
        for node in self.node1.iter():
            self.assertEquals(node.name, items[i])
            i += 1
    
    def testChildAdd(self):
        '''
        Test to see if adding a child item works as it should.
        '''
        items = ['elephant', 'rat']
        new_node1 = Node('elephant')
        new_node2 = Node('rat')
        i = 0
        
        self.node1.child = new_node1
        new_node1.parent = self.node1
        
        new_node1.next = new_node2
        new_node2.prev = new_node1
        
        for node in self.node1.child.iter():
            self.assertEquals(node.name, items[i])
            i += 1
    
    def testGetPath(self):
        '''
        Test to see if paths are generated as expected.
        '''
        self.assertEquals(self.node1.get_path(), '/test1/command11/')
        self.assertEquals(self.node11.get_path(), '/test1/command11/')
        self.assertEquals(self.node2.get_path(), '/test2/test21/')
        self.assertEquals(self.node21.get_path(), '/test2/test21/')
        self.assertEquals(self.node22.get_path(), '/test2/test22/command221/')
        self.assertEquals(self.node23.get_path(), '/test2/test23/command231/')
        self.assertEquals(self.node221.get_path(), '/test2/test22/command221/')
        self.assertEquals(self.node222.get_path(), '/test2/test22/command222/')
        self.assertEquals(self.node231.get_path(), '/test2/test23/command231/')
        self.assertEquals(self.node232.get_path(), '/test2/test23/command232/')

    def testIsActive(self):
        '''
        Test to see if node is considered active. Ie. it matches to given path
        well enough.
        '''
        request = get_request('/foo/', 'GET')
        self.assertEquals(self.node1.is_active(request), False)
        
        request = get_request('/test1/', 'GET')
        self.assertEquals(self.node1.is_active(request), True)
        
        request = get_request('/foo/', 'GET')
        self.assertEquals(self.node11.is_active(request), False)
        
        request = get_request('/test1/command11/', 'GET')
        self.assertEquals(self.node11.is_active(request), True)

#-----------FOLLOWING TESTS ARE RELATED TO NAVIGATION LOGIC (TAGS)!------------ 

    def testGetTreeDepth(self):
        '''
        Test to determine if the depth of a tree is calculated the way it
        should be.
        '''
        self.assertEquals(get_tree_depth(None), 0)
        self.assertEquals(get_tree_depth(self.node1), 1)
        self.assertEquals(get_tree_depth(self.node11), 0)
        self.assertEquals(get_tree_depth(self.node2), 2)
        self.assertEquals(get_tree_depth(self.node21), 0)
        self.assertEquals(get_tree_depth(self.node22), 1)
        self.assertEquals(get_tree_depth(self.node23), 1)
        self.assertEquals(get_tree_depth(self.node221), 0)
        self.assertEquals(get_tree_depth(self.node222), 0)
        self.assertEquals(get_tree_depth(self.node231), 0)
        self.assertEquals(get_tree_depth(self.node232), 0)

    def testHasCommands(self):
        '''
        Test to determine whether or not a node contains commands.
        '''
        self.assertEquals(contains_commands(self.node1), True)
        self.assertEquals(contains_commands(self.node11), False)
        self.assertEquals(contains_commands(self.node2), False)
        self.assertEquals(contains_commands(self.node21), False)
        self.assertEquals(contains_commands(self.node22), True)
        self.assertEquals(contains_commands(self.node23), True)
        self.assertEquals(contains_commands(self.node221), False)
        self.assertEquals(contains_commands(self.node222), False)
        self.assertEquals(contains_commands(self.node231), False)
        self.assertEquals(contains_commands(self.node232), False)

    def testRender(self):
        '''
        Test to see if node is rendered as expected.
        '''
        request = get_request('/foo/', 'GET')
        self.assertEquals(render_node(request, self.node1),
                          '<a href="/test1/command11/">Test1</a>')
        
        request = get_request('/test1/command11/', 'GET')
        self.assertEquals(render_node(request, self.node1),
                          '<span>Test1</span>')
        
        request = get_request('/foo/', 'GET')
        self.assertEquals(render_node(request, self.node11),
                          '<a href="/test1/command11/">Command11</a>')
        
        request = get_request('/test1/command11/', 'GET')
        self.assertEquals(render_node(request, self.node11),
                          '<span>Command11</span>')

#------------------------------URL PATTERN TESTS------------------------------- 

    def testAddPathsToURLPatterns(self):
        '''
        Test to see if URL patterns are generated properly.
        '''
        regex_list = ['^$', '^test1/command11/$',
                      '^test2/test21/$',
                      '^test2/test22/command221/$',
                      '^test2/test22/command222/$',
                      '^test2/test23/command231/$',
                      '^test2/test23/command232/$']
        
        urlpatterns = patterns('navigation.views', (r'^$', 'test'),)
        
        self.assertEquals(self.node1.get_path(), '/test1/command11/')
        self.assertEquals(self.node11.get_path(), '/test1/command11/')
        self.assertEquals(self.node2.get_path(), '/test2/test21/')
        self.assertEquals(self.node21.get_path(), '/test2/test21/')
        self.assertEquals(self.node22.get_path(), '/test2/test22/command221/')
        self.assertEquals(self.node23.get_path(), '/test2/test23/command231/')
        self.assertEquals(self.node221.get_path(), '/test2/test22/command221/')
        self.assertEquals(self.node222.get_path(), '/test2/test22/command222/')
        self.assertEquals(self.node231.get_path(), '/test2/test23/command231/')
        self.assertEquals(self.node232.get_path(), '/test2/test23/command232/')
        
        add_paths_to_urlpatterns(urlpatterns, self.node1)
        
        i = 0
        for pattern in urlpatterns:
            regex = repr(pattern).split(' ')[-1][:-1]
            self.assertEquals(regex, regex_list[i])
            i += 1

class NodeTreeTestCase(TestCase):
    '''
    These tests cover reading of YAML definition file and parsing it to a tree.
    '''
    def testCheckNode(self):
        '''
        Test to see if check_node adds item to a tree as it should.
        '''
        root_node = None
        current_node = None
        
        current_node, root_node = check_node(current_node, root_node, 'cat')
        
        self.assertNotEquals(root_node, None)
        self.assertNotEquals(current_node, None)
        self.assertEquals(root_node.name, 'cat')
        self.assertEquals(root_node, current_node)
    
    def testReadYaml(self):
        '''
        Test to see if YAML is read.
        '''
        yaml_parsed = read_yaml(STRUCTURE_PATH).values()[TABS]
        
        self.assertEquals(yaml_parsed[0]['tab'], 'noticeboard')
    
    def testGetNavigationRoot(self):
        '''
        Test to see if root of navigation is returned properly.
        '''
        tabs = None
        get_navigation_root(tabs, TABS)
        self.assertEquals(tabs, None)
        
        tabs = read_yaml(STRUCTURE_PATH).values()[TABS]
        tabs = get_navigation_root(None, TABS)
        
        print tabs
        self.assertEquals(tabs.name, 'noticeboard')
    
    def testGetPaths(self):
        '''
        Test to see if nodes return proper paths.
        
        get_path is tested earlier. This test operates on parsed structure
        which makes the case a bit different and hence worth testing.
        '''
        tabs = get_tabs()
        self.assertEquals(tabs.get_path(), '/noticeboard/')
        self.assertEquals(tabs.next.child.get_path(),
                          '/planning/day/browse/')
        self.assertEquals(tabs.next.child.child.get_path(),
                          '/planning/day/browse/')
    
    def testGetTabs(self):        
        '''
        Test to see if node names match, tab case.
        '''
        tabs = get_tabs()
        self.assertEquals(tabs.name, 'noticeboard')
        self.assertEquals(tabs.next.name, 'planning')
        self.assertEquals(tabs.next.prev.name, 'noticeboard')
        self.assertEquals(tabs.next.child.name, 'day')
        self.assertEquals(tabs.next.child.parent.name, 'planning')
        self.assertEquals(tabs.next.child.child.name, 'browse')
        self.assertEquals(tabs.next.child.next.name, 'week')

    def testGetUserControl(self):
        '''
        Test to see if node names match, navigation case.
        '''
        user_control = get_user_control()
        self.assertEquals(user_control.name, 'settings')
        self.assertEquals(user_control.next.name, 'help')
        self.assertEquals(user_control.next.next.name, 'common')
        self.assertEquals(user_control.next.next.next.name, 'logout')

    def testIsActive(self):
        '''
        Test to see if given node is active.
        
        is_active is tested earlier. This test makes sure it works in parsed
        case too.
        '''
        tabs = get_tabs()
        
        request = get_request('foo', 'GET')
        self.assertEquals(tabs.is_active(request), False)
        
        request = get_request('/ilmoitustaulu/', 'GET')
        self.assertEquals(tabs.is_active(request), True)
        
        node = tabs.next.child
        request = get_request('/suunnittelu/paiva/', 'GET')
        self.assertEquals(node.is_active(request), True)
        
        node2 = tabs.next.child.next
        request = get_request('/foo/', 'GET')
        self.assertEquals(node2.is_active(request), False)
        
        request = get_request('/suunnittelu/viikko/', 'GET')
        self.assertEquals(node2.is_active(request), True)
