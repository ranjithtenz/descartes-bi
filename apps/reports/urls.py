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

from django.conf.urls.defaults import *

urlpatterns = patterns('reports.views',
    url(r'^ajax/report/(?P<report_id>\d+)/$', 'ajax_report', (), 'ajax_report_view'),

    url(r'^ajax/filter_form/(?P<report_id>\d+)/$', 'ajax_filter_form', (), 'ajax_filter_form_view'),
    url(r'^ajax/report_description/(?P<report_id>\d+)/$','ajax_report_description', (), 'ajax_report_description_view'),
    url(r'^ajax/report_validation/(?P<report_id>\d+)/$','ajax_report_validation', (), 'ajax_report_validation_view'),
    url(r'^ajax/report/(?P<report_id>\d+)/benchmarks/$', 'ajax_report_benchmarks', (), 'ajax_report_benchmarks_view'),

    #url(r'^dashboard/$', 'django.views.generic.simple.direct_to_template', { 'template' : 'dashboard.html'}, 'dashboard'),	
)
