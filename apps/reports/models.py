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

from django.db import models
import datetime

from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from django.utils.translation import ugettext_lazy as _
        
FILTER_TYPE_DATE  = u'DA'
FILTER_TYPE_COMBO = u'DR'
FILTER_TYPE_MONTH = u'MO'
        
        
class Filter(models.Model):
    FILTER_FIELD_CHOICES = (
        (FILTER_TYPE_DATE, _(u'Date field')),
        (FILTER_TYPE_COMBO, _(u'Simple drop down')),
#		(u'SE', _(u'Separator  *N/A*')),
#		(u'DQ', _(u'Simple drop down from query *N/A*')),
#		(u'SI', _(u'Drop down with hidden index  *N/A*')),
#		(u'SI', _(u'Drop down with hidden index from query *N/A*')),
#		(u'TX', _(u'Text field *N/A*')),
#		(u'NU', _(u'Number field *N/A*')),
#		(u'MO', _(u'Month name drop down *N/A*')),
    )
    name = models.CharField(max_length = 48, help_text = _(u"Name of the parameter to be used in the queries.  Do not use spaces or special symbols."), verbose_name = _(u"name"))
    description = models.CharField(max_length = 32, blank = True, null = True, verbose_name = _(u"description"))
    type = models.CharField(max_length = 2, choices = FILTER_FIELD_CHOICES, verbose_name = _(u"type"))
    label = models.CharField(max_length = 32, help_text = "Text label that will be presented to the user.", verbose_name = _(u"label"))
    default = models.CharField(max_length = 32, blank = True, null = True, help_text = "Defautl value or one the special functions [this_day, this_month, this_year].", verbose_name = _(u"default"))
    options = models.TextField(blank = True, null = True, verbose_name = _(u"options"))
    
    def __unicode__(self):
        if self.description:
            return '%s "%s"' % (self.name, self.description)
        else:
            return self.name
        
    def get_parents(self):
        return ', '.join(['"%s"' % p.name for p in self.filterset_set.all()])
    get_parents.short_description = _(u'used by filter sets')
    
    def execute_function(self):
        today = datetime.date.today()
        if self.default == 'function:this_day':
            self.default = today
            
        if self.default == 'function:this_month':
            self.default = datetime.date(today.year, today.month, 1)
            
        if self.default == 'function:this_year':
            self.default = datetime.date(today.year, 1, 1)

    class Meta:
        ordering = ['name']
        verbose_name = _(u"filter")
        verbose_name_plural = _(u"filters")			
           
            
class Filterset(models.Model):
    name = models.CharField(max_length = 64, verbose_name = _(u"name"), help_text = _(u'A simple name for your convenience.'))
    filters = models.ManyToManyField(Filter, through='FilterExtra', verbose_name = _(u"filters"))
    
    def __unicode__(self):
        return self.name

    def get_parents(self):
        return ', '.join(['"%s"' % r.title for r in self.report_set.all()])		
    get_parents.short_description = _(u'used by reports')
    
    class Meta:
        ordering = ['name']
        verbose_name = _(u"filters set")
        verbose_name_plural = _(u"filters sets")			


class FilterExtra(models.Model):
    filterset = models.ForeignKey(Filterset)
    filter = models.ForeignKey(Filter, verbose_name = _(u"filter"))
    order = models.IntegerField(default = 0, verbose_name = _(u"order"))

    def __unicode__(self):
        return unicode(self.filter)
        
    class Meta:
        verbose_name = _(u"filter")
        verbose_name_plural = _(u"filters")	
        
        
class Serie(models.Model):
    name = models.CharField(max_length = 64, help_text = "Internal name.  Do not use spaces or special symbols.", verbose_name = _(u"name"))
    label = models.CharField(max_length = 24, null = True, blank = True, help_text = "Label to be shown to the user and to be used for the legend.", verbose_name = _(u"label"))
    tick_format = models.CharField(blank = True, null = True, max_length = 16, help_text = "Example: Currency - '$%d.00'", verbose_name = _(u"tick format"))
    query = models.TextField(verbose_name = _(u"query"), help_text = _(u"SQL query, that returns only 2 fields and may of may be a parameter query.  Include parameters in the format: <field> LIKE %(parameter)s.  Also the SQL wildcard character % must be escaped as %%."))
    description = models.TextField(null = True, blank = True, help_text = "Description of the query, notes and observations.", verbose_name = _(u"description"))
    
    validated = models.BooleanField(default = False, verbose_name = _(u"validated?"))
    validated_date = models.DateField(blank = True, null = True, verbose_name = _(u"validation date"))
    validated_person = models.CharField(max_length = 32, blank = True, null = True, verbose_name = _(u"validated by"))
    validation_description = models.TextField(blank = True, null = True, verbose_name = _(u"validation description"), help_text = _(u"An explanation or description about how this series was validated."))
    
    last_execution_time = models.PositiveIntegerField(blank = True, null = True)
    avg_execution_time = models.PositiveIntegerField(blank = True, null = True)
    
    def __unicode__(self):
        return self.name
        
    def get_parents(self):
        return ', '.join(['"%s"' % r.title for r in self.report_set.all()])		
    get_parents.short_description = _(u'used by reports')
    
    def get_params(self):
        import re
        return "(%s)" % ', '.join([p for p in re.compile('%\((.*?)\)').findall(self.query)])
    get_params.short_description = _(u'parameters')
    
    def get_filters(self):
        #TODO: optmize
        #return [fs for fs in [r.filtersets.all()] for r in self.report_set.all()]
        #return ', '.join(['"%s"' % f.title for f in self.report_set.all()])		

        filters = []
        for report in self.report_set.all():
            for set in report.filtersets.all():
                for filter in set.filters.all():
                    if filter not in filters:
                        filters.append(filter)
        return ' ,'.join(['%s' % f for f in filters])
    get_filters.short_description = _(u'filters')
    
    class Meta:
        ordering = ['name']
        verbose_name = _(u"serie")
        verbose_name_plural = _(u"series")			


class SeriesStatistic(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name = _(u"timestamp"))
    serie = models.ForeignKey(Serie, verbose_name = _(u"serie"))
    user = models.ForeignKey(User, verbose_name = _(u"user"))
    execution_time = models.PositiveIntegerField(verbose_name = _(u"execution time"))
    params = models.CharField(max_length = 128, blank = True, null = True, verbose_name = _(u"parameters"))

    def __unicode__(self):
        return unicode(self.id)#"%s | %s | %s" % (self.timestamp, self.serie, self.user)

    class Meta:
        ordering = ('-id',)
        verbose_name = _(u"series statistic")
        verbose_name_plural = _(u"series statistics")	
    
    
class Report(models.Model):
    CHART_TYPE_CHOICES = (
        (u'SI', _(u'Standard X,Y')),
        (u'PI', _(u'Pie chart')),
    )	
    LEGEND_LOCATION_CHOICES = (
        (u'nw', _(u'North-West')),
        (u'n', _(u'North')),
        (u'ne', _(u'North-East')),
        (u'e', _(u'East')),
        (u'se', _(u'South-East')),
        (u's', _(u'South')),
        (u'sw', _(u'South-West')),
        (u'w', _(u'West')),
    )
    ORIENTATION_CHOICES = (
        (u'h', _(u'Horizontal')),
        (u'v', _(u'Vertical')),
    )

    title = models.CharField(max_length = 128, help_text = _(u"Chart title."), verbose_name = _(u"title"))
    description = models.TextField(null = True, blank = True, help_text = _(u"A description of the report.  This description will also be presented to the user."), verbose_name = _(u"description"))
    type = models.CharField(max_length = 2, choices = CHART_TYPE_CHOICES, default = "SI", help_text = _(u"Chart type."), verbose_name = _(u"type"))
    zoom = models.BooleanField(default = False, verbose_name = _(u"zoom"), help_text = _(u"Allow the user to zoom in on the chart."))
    pointlabels = models.BooleanField(default = False, verbose_name = _(u"point labels"), help_text = _(u"Enable point labels displaying the values."))
    pointlabels_location = models.CharField(max_length = 2, default = 'n', choices = LEGEND_LOCATION_CHOICES, verbose_name = _(u"point label location"), help_text = _(u"The point label position respetive to the series."))
    trendline = models.BooleanField(default = False, help_text = _(u"Show a trendline?"), verbose_name = _(u"trendline"))
    highlighter = models.BooleanField(default = False, verbose_name = _(u"highlighter"))
    use_one_scale = models.BooleanField(default = False, help_text = _(u"This options forces all series in chart to use the same scale."), verbose_name = _(u"use one scale"))
    scale_label_override = models.CharField(max_length = 32, null = True, blank = True,help_text = _(u"The scale label to be used when using a single scale per report."), verbose_name = _(u"scale label override"))
    tracking = models.BooleanField(default = False, help_text = _(u"Draw horizontal and/or vertical tracking lines across the plot to the cursor location."), verbose_name = _(u"data tracking"))
    legend = models.BooleanField(default = False, help_text = _(u"Show legend?"), verbose_name = _(u"legend"))
    legend_location = models.CharField(max_length = 2, default = 'ne', choices = LEGEND_LOCATION_CHOICES, verbose_name = _(u"legend location"), help_text = _(u"Select the legend position respetive to the chart."))
    orientation = models.CharField(max_length = 1, default = 'v', choices = ORIENTATION_CHOICES, verbose_name = _(u"report orientation"), help_text = _(u"Direction the report's series will be drawn.")) 
    filtersets = models.ManyToManyField(Filterset, null = True, blank = True, verbose_name = _(u"filter sets"))
    series = models.ManyToManyField(Serie, through='SerieType', verbose_name = _(u"series"))
    #tracking_axis = X,Y, both

    #publish = models.BooleanField(default = False)
#	validated = models.BooleanField(default = False, verbose_name = _(u"validated?"))
#	validated_date = models.DateField(blank = True, null = True, verbose_name = _(u"validation date"))
#	validated_person = models.CharField(max_length = 32, blank = True, null = True, verbose_name = _(u"validated by"))

#	series_label = models.CharField(max_length = 32, null = True, blank = True)
#	scale_label = models.CharField(max_length = 32, null = True, blank = True)
#	series_label_rotation = models.IntegerField(default = 0)
#	scale_label_rotation = models.IntegerField(default = 90)
#	use_series_label = models.BooleanField(default = True)	


    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        return ('ajax_report_view', [str(self.id)])
    get_absolute_url = models.permalink(get_absolute_url)


    def get_parents(self):
        return ', '.join([mi.title for mi in self.menuitem_set.all()])
    get_parents.short_description = _(u"used by menus")
    
    def get_series(self):
        return ', '.join(['"%s (%s)"' % (serie.serie.name, serie.get_type_display()) for serie in self.serietype_set.all()])
    get_series.short_description = _(u"series")
    
    class Meta:
        ordering = ['title']
        verbose_name = _(u"report")
        verbose_name_plural = _(u"reports")		
        
        
class ReportStatistic(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name = _(u"timestamp"))
    report = models.ForeignKey(Report, verbose_name = _(u"report"))
    user = models.ForeignKey(User, verbose_name = _(u"user"))
    execution_time = models.PositiveIntegerField(verbose_name = _(u"execution time"))
    params = models.CharField(max_length = 128, blank = True, null = True, verbose_name = _(u"parameters"))

    def __unicode__(self):
        return unicode(self.id)#"%s | %s | %s" % (self.timestamp, self.serie, self.user)

    class Meta:
        ordering = ('-id',)
        verbose_name = _(u"report statistic")
        verbose_name_plural = _(u"report statistics")	
      
        
class SerieType(models.Model):
    SERIES_TYPE_CHOICES = (
        (u'BA', _(u'Bars')),
        (u'LI', _(u'Lines')),
    )
    serie = models.ForeignKey(Serie, verbose_name = _(u"serie"))
    report = models.ForeignKey(Report, verbose_name = _(u"chart"))
    type = models.CharField(max_length = 2, choices = SERIES_TYPE_CHOICES, default = "BA", verbose_name = _(u"type"))
    zerobase = models.BooleanField(default = True, verbose_name = _(u"zerobase"), help_text = _(u"Force this serie's scale to start at integer number 0."))
    
    def __unicode__(self):
        return unicode(self.serie)	

    class Meta:
        #ordering = ['title']
        verbose_name = _(u"serie")
        verbose_name_plural = _(u"series")	
        
        
class Menuitem(models.Model):
    #TODO: reports display order
    title = models.CharField(max_length = 64, verbose_name = _(u"title"))
    reports = models.ManyToManyField(Report, verbose_name = _(u"chart"))
    order = models.IntegerField(default = 0, verbose_name = _(u"order"))

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['order', 'title']		
        verbose_name = _(u"menu item")
        verbose_name_plural = _(u"menu items")
        
    def get_reports(self):
        return ', '.join(['"%s"' % r.title for r in self.reports.all()])
    get_reports.short_description = _(u"charts")


class UserPermission(models.Model):
    UNION_CHOICES = (
        ( 'E', _(u'Exclusive')),
        ( 'I', _(u'Inclusive')),
        ( 'O', _(u'Override')),
    )
    user = models.ForeignKey(User, unique = True)
    #access_unpublished_reports = models.BooleanField(default = False)
    union = models.CharField(max_length = 1, choices = UNION_CHOICES, default = 'I', verbose_name = _(u"Group/user permissions union type"), help_text = _(u"Determines how the user permissions interact with the group permissions of this user."))
    reports = models.ManyToManyField(Report, blank = True, null = True, verbose_name = _(u"charts"))
    filters = models.ManyToManyField(Filter, through = 'UserPermissionFilterValues', verbose_name = _(u"filters"))

    def get_reports(self):
        return ', '.join(['"%s"' % r.title for r in self.reports.all()])
    get_reports.short_description = _(u"charts")
    
    def __unicode__(self):
        return unicode(self.user)
    
    class Meta:
        verbose_name = _(u"user permission")
        verbose_name_plural = _(u"user permissions")


class UserPermissionFilterValues(models.Model):
    userpermission = models.ForeignKey(UserPermission, verbose_name = _(u"user permissions"))
    filter = models.ForeignKey(Filter, verbose_name = _(u"filter"))
    options = models.TextField(blank = True, null = True, verbose_name = _(u"options"))
    default = models.CharField(max_length = 32, blank = True, null = True, help_text = "Defautl value or one the special functions [this_day, this_month, this_year].", verbose_name = _(u"default"))
    
    def __unicode__(self):
        return "%s = %s" % (self.filter, self.options)
        
    class Meta:
        verbose_name = _(u"user filter values limit")
        verbose_name_plural = _(u"user filter values limits")
      
        
class GroupPermission(models.Model):
    group = models.ForeignKey(Group, unique=True, verbose_name = _(u"group"))
    #access_unpublished_reports = models.BooleanField(default = False)
    reports = models.ManyToManyField(Report, blank = True, null = True, verbose_name = _(u"reports"))
    filters = models.ManyToManyField(Filter, through = 'GroupPermissionFilterValues', verbose_name = _(u"filters"))

    def __unicode__(self):
        return unicode(self.group)
    
    class Meta:
        verbose_name = _(u"group permissions")
        verbose_name_plural = _(u"groups permissions")

    def get_reports(self):
        return ', '.join(['"%s"' % r.title for r in self.reports.all()])
    get_reports.short_description = _(u"charts")


class GroupPermissionFilterValues(models.Model):
    grouppermission = models.ForeignKey(GroupPermission, verbose_name = _(u"group permissions"))
    filter = models.ForeignKey(Filter, verbose_name = _(u"filter"))
    options = models.TextField(blank = True, null = True, verbose_name = _(u"options"))
    default = models.CharField(max_length = 32, blank = True, null = True, help_text = "Defautl value or one the special functions [this_day, this_month, this_year].", verbose_name = _(u"default"))

    def __unicode__(self):
        return "%s = %s" % (self.filter, self.options)
        
    class Meta:
        verbose_name = _(u"group filter values limit")
        verbose_name_plural = _(u"group filter values limits")		
