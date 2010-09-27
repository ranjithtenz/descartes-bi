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

from reports.models import FilterExtra, SerieType, \
    GroupPermissionFilterValues, UserPermissionFilterValues, \
    UserPermission, GroupPermission, Report, Serie, Filterset, Filter, \
    Menuitem, SeriesStatistic, ReportStatistic
    
from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields import CharField

#clone_objects Copyright (C) 2009  Rune Bromer
#http://www.bromer.eu/2009/05/23/a-generic-copyclone-action-for-django-11/
def clone_objects(objects, title_fieldnames):
    def clone(from_object, title_fieldnames):
        args = dict([(fld.name, getattr(from_object, fld.name))
                for fld in from_object._meta.fields
                        if fld is not from_object._meta.pk])

        for field in from_object._meta.fields:
            if field.name in title_fieldnames:
                if isinstance(field, CharField):
                    args[field.name] = getattr(from_object, field.name) + \
                                        (" (%s) " % unicode(_(u'copy')))

        return from_object.__class__.objects.create(**args)

    if not hasattr(objects,'__iter__'):
        objects = [ objects ]

    # We always have the objects in a list now
    objs = []
    for obj in objects:
        obj = clone(obj, title_fieldnames)
        obj.save()
        objs.append(obj)


class ReadOnlyWidget(forms.Widget):
    def __init__(self, original_value, display_value):
        self.original_value = original_value
        self.display_value = display_value

        super(ReadOnlyWidget, self).__init__()

    def render(self, name, value, attrs=None):
        if self.display_value is not None:
            return unicode(self.display_value)
        return unicode(self.original_value)

    def value_from_datadict(self, data, files, name):
        return self.original_value


class ReadOnlyAdminFields(object):
    def get_form(self, request, obj=None):
        form = super(ReadOnlyAdminFields, self).get_form(request, obj)

        if hasattr(self, 'readonly'):
            for field_name in self.readonly:
                if field_name in form.base_fields:

                    if hasattr(obj, 'get_%s_display' % field_name):
                        display_value = getattr(obj, 'get_%s_display' %
                                                field_name)()
                    else:
                        display_value = None

                    form.base_fields[field_name].widget = \
                        ReadOnlyWidget(getattr(obj, field_name, ''),
                                       display_value)
                    form.base_fields[field_name].required = False

        return form


class UserPermissionFilterValuesInline(admin.StackedInline):
    model = UserPermissionFilterValues
    extra = 1
    classes = ('collapse-open',)
    allow_add = True	


class UserPermissionAdmin(admin.ModelAdmin):
    radio_fields = {'union':admin.HORIZONTAL}
    list_display = ('user', 'get_reports')
    filter_horizontal = ('reports',)
    inlines = [
        UserPermissionFilterValuesInline,
    ]
    order = 8


class GroupPermissionFilterValuesInline(admin.StackedInline):
    model = GroupPermissionFilterValues
    extra = 1
    classes = ('collapse-open',)
    allow_add = True	


class GroupPermissionAdmin(admin.ModelAdmin):
    list_display = ('group', 'get_reports')
    filter_horizontal = ('reports',)
    inlines = [
        GroupPermissionFilterValuesInline,
    ]
    order = 9


class FilterAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'type', 'label', 'default',
                    'get_parents')
    inlines = [
        GroupPermissionFilterValuesInline, UserPermissionFilterValuesInline,
    ]
    order = 0


class FilterInline(admin.StackedInline):
    model = FilterExtra
    extra = 1
    classes = ('collapse-open',)
    allow_add = True


class FiltersetAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_parents')

    inlines = [
        FilterInline,
    ]
    order = 1


class SerieAdmin(admin.ModelAdmin):
    search_fields = ['name', 'label']
    search_fields_verbose = ['Name', 'Label']
    list_display = ('name', 'label', 'get_params', 'get_parents', 'validated')
    order = 2

    fieldsets = (
            (None, {
                'fields': ('name', 'label', 'tick_format', 'query',
                           'description')
            }),
            (_(u'Validation'), {
                'classes': ('collapse-open',),
                'fields': ('validated', 'validated_date', 'validated_person',
                           'validation_description')
            }),
    )	

    actions = ['clone']

    def clone(self, request, queryset):
        clone_objects(queryset, ('name',))

        if queryset.count() == 1:
            message_bit = _(u"1 series was")
        else:
            message_bit = _(u"%s series were") % queryset.count()
        self.message_user(request, _(u"%s copied.") % message_bit)

    clone.short_description = _(u"Copy the selected object")	


class SerieInline(admin.StackedInline):
    model = SerieType
    extra = 1
    classes = ('collapse-open',)
    allow_add = True


class ReportAdmin(admin.ModelAdmin):
    radio_fields = {'type':admin.VERTICAL, 'orientation':admin.HORIZONTAL}
    list_display = ('title', 'description', 'type', 'get_series',
                    'get_parents')
    filter_horizontal = ('filtersets',)
    search_fields = ['title', 'description']
    search_fields_verbose = ['Title', 'Description']
    exclude = ('series',)
    inlines = [
        SerieInline, 
    ]
    order = 3	

    actions = ['clone']

    def clone(self, request, queryset):
        clone_objects(queryset, ('title',))

        if queryset.count() == 1:
            message_bit = _(u"1 report was")
        else:
            message_bit = _(u"%s reports were") % queryset.count()
        self.message_user(request, _(u"%s copied.") % message_bit)

    clone.short_description = _(u"Copy the selected object")	


class MenuitemAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'get_reports')
    list_editable = ('order',)	
    filter_horizontal = ('reports',)
    order = 4


class SeriesStatisticAdmin(ReadOnlyAdminFields, admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    list_filter = ['serie', 'user']
    list_display = ['id', 'timestamp', 'serie', 'user', 'execution_time',
                    'params']
    readonly = ['serie', 'user', 'execution_time', 'params']
    order = 10
    actions = None


class ReportStatisticAdmin(ReadOnlyAdminFields, admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    list_filter = ['report', 'user']
    list_display = ['id', 'timestamp', 'report', 'user', 'execution_time',
                    'params']
    readonly = ['report', 'user', 'execution_time', 'params']
    order = 11
    actions = None


admin.site.register(UserPermission, UserPermissionAdmin)
admin.site.register(GroupPermission, GroupPermissionAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Serie, SerieAdmin)
admin.site.register(Filterset, FiltersetAdmin)
admin.site.register(Filter, FilterAdmin)
admin.site.register(Menuitem, MenuitemAdmin)
admin.site.register(ReportStatistic, ReportStatisticAdmin)
admin.site.register(SeriesStatistic, SeriesStatisticAdmin)
