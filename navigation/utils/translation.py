# -*- coding: utf-8 -*-

def set_language(request):
    '''
    Sets session variable containing language to use based on the user setting.

    @param request: request to set session variable in
    '''
    # this should set language based on django lang! django translation get_language
    #user_profile = UserProfile.get(request.user)

    # XXX: hack. figure out how to fetch this from actual user (move to app?)
    request.session['django_language'] = 'fi' # user_profile.language

def get_language(request):
    '''
    Returns language stored in session should one be found. If one is not
    found, session variable is created.

    @param request: request to fetch language from
    @return: returns the selected language of the user
    '''
    if 'django_language' not in request.session:
        set_language(request)

    return request.session['django_language']
