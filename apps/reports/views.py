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
import django
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.conf import settings
from django.utils.importlib import import_module

from models import Report, Menuitem, GroupPermission, UserPermission, User, SeriesStatistic, ReportStatistic
from models import FILTER_TYPE_DATE, FILTER_TYPE_COMBO
from forms import FilterForm

import datetime
import re

def load_backend(backend_name):
	try:
		# Most of the time, the database backend will be one of the official
		# backends that ships with Django, so look there first.
		return import_module('.base', 'django.db.backends.%s' % backend_name)
	except ImportError, e:
		# If the import failed, we might be looking for a database backend
		# distributed external to Django. So we'll try that next.
		try:
			return import_module('.base', backend_name)
		except ImportError, e_user:
			# The database backend wasn't found. Display a helpful error message
			# listing all possible (built-in) database backends.
			backend_dir = os.path.join(__path__[0], 'backends')
			try:
				available_backends = [f for f in os.listdir(backend_dir)
						if os.path.isdir(os.path.join(backend_dir, f))
						and not f.startswith('.')]
			except EnvironmentError:
				available_backends = []
			available_backends.sort()
			if backend_name not in available_backends:
				error_msg = "%r isn't an available database backend. Available options are: %s\nError was: %s" % \
					(backend_name, ", ".join(map(repr, available_backends)), e_user)
				raise ImproperlyConfigured(error_msg)
			else:
				raise # If there's some other error, this must be an error in Django itself.

backend_source = load_backend(settings.SOURCE_DATABASE_ENGINE)
if django.VERSION >= (1,2):
	connection_source = backend_source.DatabaseWrapper({
		'HOST': settings.SOURCE_DATABASE_HOST,
		'NAME': settings.SOURCE_DATABASE_NAME,
		'OPTIONS': {},
		'PASSWORD': settings.SOURCE_DATABASE_PASSWORD,
		'PORT': settings.SOURCE_DATABASE_PORT,
		'USER': settings.SOURCE_DATABASE_USER,
		'ZONE': settings.TIME_ZONE,
	})
else:
	connection_source = backend_source.DatabaseWrapper({
		'DATABASE_HOST': settings.SOURCE_DATABASE_HOST,
		'DATABASE_NAME': settings.SOURCE_DATABASE_NAME,
		'DATABASE_OPTIONS': {},
		'DATABASE_PASSWORD': settings.SOURCE_DATABASE_PASSWORD,
		'DATABASE_PORT': settings.SOURCE_DATABASE_PORT,
		'DATABASE_USER': settings.SOURCE_DATABASE_USER,
		'TIME_ZONE': settings.TIME_ZONE,
	})

def ajax_report_benchmarks(request, report_id):
	#TODO: change this to get values from serie_statistics instead
	report = get_object_or_404(Report, pk=report_id)
	result = ''
	if request.user.is_staff:
		result = '<ul>'
		for s in report.series.all():
			result += "<li>%s</li><br />" % _('"%(serie)s" = Lastest run: %(last)ss; Average: %(avg)ss') % {'serie':s.label or unicode(s), 'last':s.last_execution_time or '0', 'avg':s.avg_execution_time or '0'}
			
		result += '</ul>'

	return HttpResponse(result)
	
def ajax_filter_form(request, report_id):
	#TODO: access control
	if request.method == 'GET':
		query = request.GET

	report = get_object_or_404(Report, pk=report_id)

	if report not in _get_allowed_object_for_user(request.user)['reports']:
		return render_to_response('messagebox-error.html',
		{'title':_(u'Permission error'),
		 'message':_(u"Insufficient permissions to access this area.")})
	
	if query:
		filter_form = FilterForm(report.filtersets.all(), request.user, query)
	else:
		filter_form = FilterForm(report.filtersets.all(), request.user)
		
		
	return render_to_response('filter_form_subtemplate.html', {'filter_form':filter_form},
		context_instance=RequestContext(request))

def ajax_report_description(request, report_id):
	report = get_object_or_404(Report, pk=report_id)
	
	result = "<strong>%s</strong><br />%s" % (report.title, report.description or '')
	return HttpResponse(result)
			
def ajax_report_validation(request, report_id):                
	report = get_object_or_404(Report, pk=report_id)
	
	result = ''
	
	for s in report.series.all():
		if s.validated:
				
			result += "<li>'%s' validated on %s" % (s.label or unicode(s),
													s.validated_date)
			if s.validated_person:
				result += " by %s" % s.validated_person
			result += '</li><br />'
		
	if result:
		return HttpResponse('<ul>%s</ul>' % result)
	else:
		return HttpResponse(_(u'No element of this report has been validates.'))

def ajax_report(request, report_id):
	start_time = datetime.datetime.now()

	report = get_object_or_404(Report, pk=report_id)
	
	if report not in _get_allowed_object_for_user(request.user)['reports']:
		return render_to_response('messagebox-error.html',
		 {'title':_(u'Permission error'),
		  'message':_(u"Insufficient permissions to access this area.")})
	
	output_type = request.GET.get('output_type', 'chart')
	params = {}
	special_params = {}

	if report.filtersets.all():
		filtersets = report.filtersets
		if request.method == 'GET':
			filter_form = FilterForm(filtersets, request.user, request.GET)
		else:
			filter_form = FilterForm(filtersets, request.user)

		valid_form = filter_form.is_valid()

		for set in filtersets.all():
			for filter in set.filters.all():

				if filter_form.is_valid():
					value = filter_form.cleaned_data[filter.name]
					if not value:
						filter.execute_function()
						value = filter.default

				else:
					filter.execute_function()
					value = filter.default

				if filter.type == FILTER_TYPE_DATE:
					params[filter.name] = value.strftime("%Y%m%d")
				elif filter.type == FILTER_TYPE_COMBO:
					special_params[filter.name] = '(' + ((''.join(['%s'] * len(value)) % tuple(value))) + ')'
				else:
					params[filter.name] = value

	series_results = []
	labels = []
	for s in report.serietype_set.all():
		query = s.serie.query
		if re.compile("[^%]%[^%(]").search(query):
			return render_to_response('messagebox-error.html', {'title':_(u'Query error'), 'message':_(u"Single '%' found, replace with double '%%' to properly escape the SQL wildcard caracter '%'.")})		

		cursor = connection_source.cursor()

		if special_params:
			for sp in special_params.keys():
				query = re.compile('%\(' + sp +'\)s').sub(special_params[sp], query)
			try:
				serie_start_time = datetime.datetime.now()
				cursor.execute(query, params)
			except: 
				import sys
				(exc_type, exc_info, tb) = sys.exc_info()
				return render_to_response('messagebox-error.html', {'title':exc_type, 'message':exc_info})

		else:
			cursor.execute(query, params)
			serie_start_time = datetime.datetime.now()
			
		labels.append(re.compile('aS\s(\S*)', re.IGNORECASE).findall(query))
		
		if output_type == 'chart':
			series_results.append(data_to_js_chart(cursor.fetchall(), s.serie.tick_format, report.orientation))
		elif output_type == 'grid':
			series_results.append(data_to_js_grid(cursor.fetchall(), s.serie.tick_format))

		s.serie.last_execution_time = (datetime.datetime.now() - serie_start_time).seconds
		s.serie.avg_execution_time = (s.serie.avg_execution_time or 0 + s.serie.last_execution_time) / 2
		s.serie.save()
		
		try:
			serie_statistics = SeriesStatistic()
			serie_statistics.serie = s.serie
			serie_statistics.user = request.user
			serie_statistics.execution_time = (datetime.datetime.now() - serie_start_time).seconds
			serie_statistics.params = ', '.join(["%s = %s" % (k, v) for k, v in filter_form.cleaned_data.items()])
			serie_statistics.save()
		except:
			pass

	try:
		report_statistics = ReportStatistic()
		report_statistics.report = report
		report_statistics.user = request.user
		report_statistics.execution_time = (datetime.datetime.now() - start_time).seconds
		report_statistics.params = "%s" % (', '.join(["%s = %s" % (k, v) for k, v in filter_form.cleaned_data.items()]))
		report_statistics.save()
	except:
		pass
		
	if report.orientation == 'v':
		h_axis = "x"
		v_axis = "y"
	else:
		h_axis = "y"
		v_axis = "x"
		
	data = {
		'chart_data': ','.join(series_results),
		'series_results': series_results,
		'chart_series' : report.serietype_set.all(),
		'chart' : report,
		'h_axis' : h_axis,
		'v_axis' : v_axis,
		'ajax' : True,
		'query' : query,
		'params' : params,
		'series_labels': labels,
		'time_delta' : datetime.datetime.now() - start_time,
	}

	if output_type == 'chart':
		return render_to_response('single_chart.html', data,
			context_instance=RequestContext(request))
	elif output_type == 'grid':
		return render_to_response('single_grid.html', data,
			context_instance=RequestContext(request))
	else:
		return render_to_response('messagebox-error.html', {'title':_(u'Error'), 'message':_(u"Unknown output type (chart, table, etc).")})

#TODO: Improve this further
def data_to_js_chart(data, label_format = None, orientation = 'v'):
	if not data:
		return ''

	if not label_format:
		label_format = "%s"
		
	result = '['

	if orientation == 'v':
		for key, value in data:
			result += '["%s",%s,"%s"],' % (key or '?', value, label_format % value)
			#result = [[k or '?',v, label_formar % v] for k,v in a]
	else:
		for key, value in data:
			try:
				# unicode(key.decode("utf-8")) Needed to handle non ascii
				result += '[%s,"%s","%s"],' % (value,
					  unicode(key.decode("utf-8")) or u'?', unicode(value))
			except:
				#However fails with long integer
				result += '[%s,"%s","%s"],' % (value, unicode(key or '?'),
						unicode(value))
			
	result = result[:-1]
	result += ']'
		
	return result

def data_to_js_grid(data, label_format = None):
	if not data:
		return ''
		
	if not label_format:
		label_format = "%s"
		
	result = '['
	for key, value in data:
		result += '{key:"%s", value:"%s"},' %  (key or '?', label_format % value)

	result = result[:-1]
	result += ']'
		
	return result
	
def acl(request):
	aclform = ACLForm()
	return render_to_response('acl.html', {
		'aclform' : aclform,
		},
		context_instance=RequestContext(request))	

def _get_allowed_object_for_user(user):
	reports_allowed = []
	menuitems_allowed = []
	try:
		if type(user) == type(''):
			user = User.objects.get(username=user)

		#staff gets all reports & menuitems
		if user.is_staff:
			return {
				'reports':Report.objects.all(),
				'menuitems':Menuitem.objects.all()
			}

		for group in user.groups.all():
			try:
				gp = GroupPermission.objects.get(group=group)
				for report in gp.reports.all():
					if report not in reports_allowed:
						reports_allowed.append(report)

			except:
				#Group does have permissions
				pass
		try:
			up = UserPermission.objects.get(user=user)
			if up.union == 'O':  #Overwrite
				reports_allowed = []

			if up.union == 'I' or up.union == 'O': #Inclusive
				for report in up.reports.all():
					if report not in reports_allowed:
						reports_allowed.append(report)
			elif up.union == 'E':  #Exclusive
				for report in up.reports.all():
					if report in reports_allowed:
						reports_allowed.remove(report)
			
		except:
			#Not User permission for this user
			pass
	except:
		#unkown user or anonymous
		pass

	for report in reports_allowed:
		menuitems = report.menuitem_set.all()
		for menuitem in menuitems:
			if menuitem not in menuitems_allowed:
				menuitems_allowed.append(menuitem)

	return {
		'reports':reports_allowed,
		'menuitems':menuitems_allowed
		}

#TODO: Define filter default value when user is doing an exclusive union
def _get_user_filters_limits(user):
	filter_limits = {}
	try:
		if type(user) == type(''):
			user = User.objects.get(username=user)

		#staff gets no limits
		if user.is_staff:
			return filter_limits

		for group in user.groups.all():
			try:
				gp = GroupPermission.objects.get(group=group)
				for filter in gp.filters.all():
					if filter not in filter_limits:#.keys():
						filter_limits[filter] = {}
						
					if gp.grouppermissionfiltervalues_set.get(filter = filter).default:
						filter_limits[filter]['default'] = gp.grouppermissionfiltervalues_set.get(filter = filter).default
						
					if filter.type == FILTER_TYPE_COMBO:
						if 'mask' not in filter_limits[filter]:
							filter_limits[filter]['mask'] = list(eval(gp.grouppermissionfiltervalues_set.get(filter = filter).options, {}))
						else:
							for n in eval(gp.grouppermissionfiltervalues_set.get(filter = filter).options, {}):
								if n not in filter_limits[filter]['mask']:
									filter_limits[filter]['mask'].append(n)
			except:
				#Group does have permissions
				pass
		try:
			up = UserPermission.objects.get(user=user)

			if up.union == 'O':  #Overwrite
				filter_limits = {}

			if up.union == 'I' or up.union == 'O': #Inclusive
				for filter in up.filters.all():
					if filter not in filter_limits:#.keys():
						filter_limits[filter] = {}

					if up.userpermissionfiltervalues_set.get(filter = filter).default:
						filter_limits[filter]['default'] = up.userpermissionfiltervalues_set.get(filter = filter).default
						
					if filter.type == FILTER_TYPE_COMBO:
						if 'mask' not in filter_limits[filter]:
							filter_limits[filter]['mask'] = list(eval(up.userpermissionfiltervalues_set.get(filter = filter).options, {}))
						else:
						#if filter.type == 'DR':
							for n in eval(up.userpermissionfiltervalues_set.get(filter = filter).options, {}):
								if n not in filter_limits[filter]['mask']:
									filter_limits[filter]['mask'].append(n)
									
			elif up.union == 'E':  #Exclusive
				for filter in up.filters.all():
					if filter in filter_limits.keys():
						if filter.type == FILTER_TYPE_COMBO:
							for n in eval(up.userpermissionfiltervalues_set.get(filter = filter).options, {}):
								if n in filter_limits[filter]['mask']:
									filter_limits[filter]['mask'].remove(n)
			
		except:
			#Not User permission for this user
			pass
	except:
		#unkown user or anonymous
		pass
			
			
	#print "FILTER LIMITS: %s" % filter_limits
	return filter_limits
