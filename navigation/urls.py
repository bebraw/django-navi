# -*- coding: utf-8 -*-
"""
File for generate URLs in selected language. 
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

def add_structure(urlpatterns):
    '''
    Adds URLs to urlpatterns based on navigation structure.
    
    @param urlpatterns: urlpatterns to add structure into
    '''
    add_paths_to_urlpatterns(urlpatterns, get_tabs())
    add_paths_to_urlpatterns(urlpatterns, get_user_control())

def add_frontpage(urlpatterns, frontpage_view):
    frontpage_patterns = (r'^frontpage/$', r'^$')

    for pattern in frontpage_patterns:
        urlpatterns += patterns('', (pattern, frontpage_view))

# XXX: sort out redirection (from base to page)
def add_navigation(urlpatterns, navigation, base_view):
    for url in navigation.get_urls():
        if 'en' in url:
            template_name = url['en']
            for path in url.values():
                urlpatterns += patterns(base_view, (r'^' + path + '/$', 'page',
                    {'template_name': template_name}), )
