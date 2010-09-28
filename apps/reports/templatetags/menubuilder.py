#
#    Copyright (C) 2010  Roberto Rosario
#    This file is part of descartes-bi.
#
#    descartes-bi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    descartes-bi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with descartes-bi.  If not, see <http://www.gnu.org/licenses/>.
#

from django import template
from django.conf import settings
from django.template.loader import get_template
from django.template import Context

from reports.models import Menuitem

register = template.Library()

def build_menu(parser, token):
    """
    {% menu menu_name %}
    """
    try:
        tag_name, menu_name = token.split_contents()
    except:
        raise template.TemplateSyntaxError, \
         "%r tag requires exactly one argument" % token.contents.split()[0]
    return MenuObject(menu_name)


class MenuObject(template.Node):
    def __init__(self, menu_name):
        self.menu_name = menu_name

    def render(self, context):
        current_path = template.resolve_variable('request.path', context)
        user = template.resolve_variable('request.user', context)
        context['menuitems'] = get_items(self.menu_name, current_path, user)
        return ''


class get_menu_node(template.Node):
    def render(self, context):
        from reports.views import _get_allowed_object_for_user
        user = template.resolve_variable('request.user', context)
        
        results = _get_allowed_object_for_user(user)
        mi_order = [mi.order for mi in results['menuitems']]
        mi_order.sort()
        context['menuitems_allowed'] = [Menuitem.objects.get(order=order)
                                        for order in mi_order]
        context['reports_allowed'] = results['reports']
        return ''


@register.tag(name='get_menu')
def get_menu(parser, token):
    return get_menu_node()

@register.filter
def in_list(value, arg):
    return value in arg
    

class GetCustomAppsNode(template.Node):
    def render(self, context):
        custom_apps = getattr(settings, 'CUSTOMIZATION_APPS', [])
        context['custom_apps'] = custom_apps
        
        custom_apps_data = {}
        for app in custom_apps:
            exec "import %s" % app
            try:
                custom_apps_data[app] = eval("%s.APP_DATA" % app)
                
                if 'template_name' in custom_apps_data[app]:
                    custom_template = get_template(
                                    custom_apps_data[app]['template_name'])
                    custom_apps_data[app]['template_data'] = custom_template.render(Context(context))
            except:
                pass
        
        context['custom_apps_data'] = custom_apps_data  
    
        return ''
        
@register.tag(name='get_custom_apps')
def get_custom_apps(parser, token):
    return GetCustomAppsNode()
