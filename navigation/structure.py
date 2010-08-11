# -*- coding: utf-8 -*-
"""
Structure utils.
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
import inspect
import os
import sys
import unicodedata
from lib.pynu import TreeNode
from django.conf import settings
from django.utils import translation


class Configuration:
    options = {'pages': (), 'hidden_pages': (), 'order': (),
        'exclusive_to': (), 'page_itself': False}

    def __init__(self, package_path):
        # XXX: this expects that the app is always named as app
        app_path = package_path.split('app' + os.sep)[-1]
        package_name = 'app.' + app_path.replace(os.sep, '.')

        self.name = package_name.split('.')[-1]

        pkg = ()
        try:
            __import__(package_name)

            pkg = sys.modules[package_name]
        except ImportError as e:
            print 'Conf fail!', e, package_name # XXX: log instead

        configuration = {}
        if 'configuration' in dir(pkg):
            configuration = pkg.configuration

        for option_name, default_value in self.options.items():
            option_value = default_value

            if option_name in configuration:
                option_value = configuration[option_name]

            setattr(self, option_name, option_value)


def languages():
    return [code for code, name in settings.LANGUAGES]

def translate(text, language):
    try:
        translation.activate(language)
        return translation.ugettext(text)
    except:
        pass


class Translated(dict):
    def __init__(self, item):
        super(Translated, self).__init__()

        for language in languages():
            self[language] = translate(item, language)


class NavigationStructure(TreeNode):
    def __init__(self, name):
        super(NavigationStructure, self).__init__()

        self.name = name
        self.url = dict()


class NavigationNode(TreeNode):
    def __init__(self, name):
        super(NavigationNode, self).__init__()

        self.name = Translated(name)
        self.view = None

    @property
    def url(self):
        return dict()


class Base(NavigationNode):
    def __init__(self, name, exclusive_to):
        super(Base, self).__init__(name)

        self.exclusive_to = exclusive_to


class Page(NavigationNode):
    def __init__(self, name, base_path, visible=True):
        super(Page, self).__init__(name)

        self.visible = visible

        self._url = dict()

        self._init_view(base_path)
    
    def _init_view(self, base_path):
        # XXX: this expects that the app is always named as app
        app_path = base_path.split('app' + os.sep)[-1]
        views_module_name = 'app.' + app_path.replace(os.sep, '.') + '.views'

        try:
            __import__(views_module_name)
        except ImportError as e:
            print 'Page conf fail!', e # XXX: log instead
            return

        views_module = sys.modules[views_module_name]
        funcs = inspect.getmembers(views_module, inspect.isfunction)
        
        def to_dict(funcs):
            ret = {}
            
            for k, v in funcs:
                ret[k] = v
            
            return ret
        
        funcs = to_dict(funcs)

        # XXX: use last fragment of url instead?
        func_name = self.name['en'].replace(' ', '_')

        self.view = funcs[func_name] if func_name in funcs else None

    @property
    def url(self):
        if not self._url:
            self._construct_urls()

        return self._url

    def _construct_urls(self):
        # XXX: pynu returns reference to container instead of true parent!!!
        parent = self.parent[0]

        if isinstance(parent, NavigationStructure):
            for lang, item in self.name.items():
                self._url[lang] = self._slugify(item)
        else:
            for lang, item in self.name.items():
                self._url[lang] = self._slugify(parent.name[lang]) + '/' + \
                    self._slugify(item)

    def _slugify(self, item):
        ret = item.lower().replace(u' ', u'_')
        
        return unicodedata.normalize('NFKD', ret).encode('ascii', 'ignore')

    @property
    def exclusive_to(self):
         # XXX: see above
         parent = self.parent[0]

         if isinstance(parent, NavigationStructure):
             return ()
         else:
             return parent.exclusive_to


#http://code.activestate.com/recipes/52558-the-singleton-pattern-implemented-with-python/#c7
class _Navigation(NavigationNode):
    _path = None

    def __init__(self):
        super(_Navigation, self).__init__(None)

    def find_node(self, url):
        url = url.strip('/')

        for node in self.walk():
            for node_url in node.url.values():
                if node_url == url:
                    return node

    def get_navigation(self, name):
        for navigation_structure in self.children:
            if navigation_structure.name == name:
                return navigation_structure

    def get_urls(self):
        return [node.url for node in self.walk()]

    def get_base_names(self):
        ret = []

        for navigation_structure in self.children:
            for base in navigation_structure.children:
                ret.append(base.name)

        return ret

    def get_page_names(self):
        ret = []

        for navigation_structure in self.children:
            for base in navigation_structure.children:
                for page in base.children:
                    ret.append(page.name)

        return ret

    def parse(self, file_path):
        def get_directory():
            return os.path.dirname(os.path.realpath(file_path))

        if not os.path.isdir(file_path):
            path = get_directory()
        else:
            path = file_path

        # XXX: make this update automatically if the directory contents have changed!
        if path != self._path:
            self._path = path

            self._parse()

    def _parse(self):
        for navi_name in os.listdir(self._path):
            navi_path = os.path.join(self._path, navi_name)

            if os.path.isdir(navi_path):
                navigation_structure = NavigationStructure(navi_name)

                conf = Configuration(navi_path)

                self._parse_bases(navigation_structure, conf, navi_path)

                self.children.append(navigation_structure)

    def _parse_bases(self, navigation_structure, conf, navi_path):
        print dir(conf)
        if conf.order:
            for folder_name in conf.order:
                base_path = os.path.join(navi_path, folder_name)
                conf = Configuration(base_path)

                if conf.page_itself:
                    page = Page(conf.name, base_path)
                    navigation_structure.children.append(page)
                else:
                    base = Base(conf.name, conf.exclusive_to)
                    navigation_structure.children.append(base)
                    self._parse_pages(base, base_path, conf)

        # XXX: else case: pick bases as they are found

    def _parse_pages(self, base, base_path, conf):
        def append_pages(pages, visible):
            for page_name in pages:
                base.children.append(Page(page_name, base_path, visible=visible))

        append_pages(conf.pages, visible=True)
        append_pages(conf.hidden_pages, visible=False)

_navigation = _Navigation()

def Navigation():
    return _navigation
