# -*- coding: utf-8 -*-
"""
File for generating URLs in selected language.
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
#from logging import debug
from django.http import HttpResponseForbidden, HttpResponseRedirect
from utils.http import default_response
from utils.session import set_variable
from structure import Navigation
from utils import translation


def user_is_authorized_to_access(request, node):
    if node.exclusive_to:
        for group_name in node.exclusive_to:
            belongs_to_group = request.user.groups.filter(name=group_name).count()

            if belongs_to_group:
                return True
    else:
        return True

def fetch_get_params(request, get_items):
    if request.method == 'GET':
        if get_items:
            kv_pairs = get_items.split('&')

            for pair in kv_pairs:
                try:
                    k, v = pair.split('=')
                except:
                    continue

                if v == 'null':
                    v = None

            set_variable(request, k, v)

def fetch_post_params(request):
    if request.method == 'POST':
        for key, value in request.POST.iteritems():
            set_variable(request, key, value)

def url_is_translatable(url, node, lang):
    return node.url[lang] != url.strip('/')

def translate_url(node, lang):
    return HttpResponseRedirect('/' + node.url[lang])

def page(request, template_name, forbidden_page):
    request_path = request.get_full_path()

    parts = request_path.split('?')

    if len(parts) > 1:
        base_url = parts[0]
        get_params = parts[1]
    else:
        base_url = request_path
        get_params = None

    navi = Navigation()
    node = navi.find_node(base_url)

    if not user_is_authorized_to_access(request, node):
        return HttpResponseForbidden(forbidden_page)

    fetch_get_params(request, get_params)
    fetch_post_params(request)

    lang = translation.get_language(request)
    if url_is_translatable(base_url, node, lang):
        return translate_url(node, lang)

    if node.view:
        return node.view(request, template_name)

    return default_response(request, template_name)
