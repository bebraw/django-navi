# -*- coding: utf-8 -*-
"""
File for session management functions.
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
LOCAL_VARIABLES = 'local_variables'

def set_variable(request, key, value):
    '''
    Set a local session variable.
    
    @param request: request to set local session variable in
    @param key: key of the variable
    @param value: value of the variable
    '''
    if LOCAL_VARIABLES not in request.session:
        request.session[LOCAL_VARIABLES] = {}
    
    if type(value) is list and len(value) == 1 and key[-2:] != '[]':
        value = value[0]
    
    request.session[LOCAL_VARIABLES][key] = value
    # this needs to be set so that Django saves the modification!
    request.session.modified = True 
