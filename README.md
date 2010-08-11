# Django-navi - Navigation plugin for Django

This plugin provides means to structure a Django project in a more hierarchical
manner. This makes it possible to abstract out and separate certain
functionality such as authentication and authorization and outlook of
navigation. In addition it automates certain functionality, such as generation
and translation of URLs and navigation, altogether.

## Project Structure

A project using this plugin may be structured as follows:
* &lt;django project&gt;
* &lt;django project&gt;/app
* &lt;django project&gt;app/__init__.py
* &lt;django project&gt;/app/models.py
* &lt;django project&gt;/app/urls.py
* &lt;django project&gt;/app/views.py
* &lt;django project&gt;/app/templates
* &lt;django project&gt;/app/&lt;base&gt;/&lt;base&gt;/.../[__init__.py, views.py]

## Plugin Initialization

In addition the plugin has to be initialized at the app urls.py and views.py
like this:

urls.py:
    from django.conf.urls.defaults import patterns
    from navigation import urls
    from navigation.structure import Navigation

    urlpatterns = patterns('',
        (r'^login/$', 'django.contrib.auth.views.login',
            {'template_name': 'login.html'}),
    )

    navigation = Navigation()
    navigation.parse(__file__)

    urls.add_frontpage(urlpatterns, 'app.views.frontpage')
    urls.add_navigation(urlpatterns, navigation, 'app.views')

views.py:
    from django.http import HttpResponseRedirect
    from django.contrib.auth.decorators import login_required
    from django.utils.translation import ugettext as _
    from navigation import views

    FRONT_PAGE = '/index/'

    @login_required
    def page(request, template_name):
        forbidden_page = '<h1>' + _('Request denied.') + '</h1>'
        return views.page(request, template_name, forbidden_page)

    def frontpage(request):
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/login/')

        return HttpResponseRedirect(FRONT_PAGE)

"page" is a special view that is called before any page is rendered. In this
case it has been protected using login_required decorator. This means that
it's not possible to access any page of the site, except for the frontpage,
without logging in first.

If "page" is valid it calls the possible view function found within the
application structure.

## Configuration

As mentioned earlier the application structure has been designed to be
hierarchical. The structure is inferred directly from Python packaging.

Suppose you have defined your app as follows:
* /app/primary
* /app/primary/blog
* /app/primary/gallery
* /app/secondary

As usual each package should contain __init__.py to mark it as a package. In
this case __init__ is used to provide additional configuration as well.
__init__.py of /app/primary might look like this:

    configuration = {
        'order': ('gallery', 'blog' ),
    }

Items will be ordered alphabetically by default. In this case it has been
decided that gallery should appear within the structure first.

I have listed pages and other configuration options below:
* hidden_pages - Tuple of pages, marked hidden (this information can be used
while generating user interface for navigation)
* pages - Tuple of pages, all visible by default
* order - Ordering of children bases. Given as a tuple.
* exclusive_to - Django user groups to which the visibility of the base has
been restricted to. Given as a tuple.
* page_itself - Flag to set a base to be a page itself (XXX: eliminate this!)

## Navigation User Interface

Note that the scheme makes it possible to generate navigation user interface
quite easily. Here's a quick example of a template tag:

    @register.simple_tag
    def get_secondary(request):
        h = HTML()
        navigation = Navigation()

        with h.ul(id="secondary_navigation"):
            if len(navigation.children) > 1:
                for page in navigation.get_navigation('secondary').children:
                    with h.li:
                        lang = translation.get_language(request)
                        name = page.name[lang].capitalize()
                        h.a(href='/' + page.url[lang]).text(name)

        return unicode(h)

## TODO

- get rid of page_itself (if there are no children packages nor "pages", mark
as page)
- write a proper demo project (project should show how to build the project
itself. Figure out how to set up virtualenv with fabric!)
- set up requirements.txt for pip (django, pynu (get rid of lib))
- write setup.py
