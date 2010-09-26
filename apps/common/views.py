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

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.template import Context
from django.conf import settings
from django.template import loader, RequestContext
from django import http

def error500(request, template_name = '500.html'):
	#TODO: if user is admin include debug info
	t = loader.get_template(template_name)

	return http.HttpResponseServerError(t.render(RequestContext(request, {
		'project_name' : settings.PROJECT_TITLE })))

def get_svn_revision(path=None):
	import os, re
	rev = None
	entries_path = '%s/.svn/entries' % path

	if os.path.exists(entries_path):
		entries = open(entries_path, 'r').read()
		# Versions >= 7 of the entries file are flat text.  The first line is
		# the version number. The next set of digits after 'dir' is the revision.
		if re.match('(\d+)', entries):
			rev_match = re.search('\d+\s+dir\s+(\d+)', entries)
			if rev_match:
				rev = rev_match.groups()[0]
		# Older XML versions of the file specify revision as an attribute of
		# the first entries node.
		else:
			from xml.dom import minidom
			dom = minidom.parse(entries_path)
			rev = dom.getElementsByTagName('entry')[0].getAttribute('revision')

	if rev:
		return u'svn-r%s' % rev
	return u'svn-unknown'
	
def set_language(request):
	if request.method == "GET":
		request.session['django_language'] = request.GET.get('language', 'en')

	return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

def home(request):
	return render_to_response('home.html', {},
		context_instance=RequestContext(request))		

def about(request):
	import settings
	
	return render_to_response('about.html', { 'revision' : get_svn_revision(settings.PROJECT_ROOT ) },
		context_instance=RequestContext(request))	
		
def get_project_root():
	from django.conf import settings
	import os
	""" get the project root directory """
	settings_mod = __import__(settings.SETTINGS_MODULE, {}, {}, [''])
	return os.path.dirname(os.path.abspath(settings_mod.__file__))	

@login_required
def dbbackup(request):
#	from django_extensions.management.commands import dumpscript
	import os
	import datetime

	from django.core.servers.basehttp import FileWrapper
	from django.conf import settings
	from django.core.files import File

	import tempfile
	import dumpscript	
	
	ct = datetime.datetime.now()
	
	if not (request.user.is_authenticated() and request.user.is_staff):
		raise http.Http404
	
	models = dumpscript.get_models(['reports','replicate','auth'])

	context = {}
	
	filename = "%s-backup-%s.py" % (settings.PROJECT_TITLE, ct.strftime("%Y-%m-%d"))
	filepath = "/tmp/%s" % filename
	f = open(filepath, 'w')
	f.write(unicode(dumpscript.Script(models=models, context=context)))
	f.close()

	f = open(filepath, 'r')
	response = HttpResponse(FileWrapper(File(f)))
	response['Content-Disposition'] = 'attachment; filename=%s' % filename
	response['Content-Length'] = os.path.getsize(filepath)
	return response

@login_required
def dbrestore(request):
	from forms import UploadFileForm
	error_message = ''
	error_title = ''
	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			try: 
				_handle_restore_file(request.FILES['file'])
				return HttpResponseRedirect('/')
			except:
				import sys
				(exc_type, exc_info, tb) = sys.exc_info()
				error_title = exc_type
				error_message = exc_info

	else:
		form = UploadFileForm()
	return render_to_response('dbrestore.html', {
		'form': form,
		'error_title' : error_title,
		'error_message' : error_message
		}, context_instance=RequestContext(request))	

def _handle_restore_file(uploaded_file):
	import sys
	import os.path
	from django.core.management.commands import reset
	import runscript

	#Turn into a real file
	dest_path = "%s/scripts/%s" % (get_project_root(), uploaded_file)
	destination = open(dest_path, 'wb+')
	for chunk in uploaded_file.chunks():
		destination.write(unicode(chunk))
	destination.close()
	
	#Erase all data from application
	r = reset.Command()
	try:
		r.handle('reports')
		r.handle('replicate')
		r.handle('auth')
	except:
		raise
		
	r = runscript.Command()
	try:
		#Remove trailing ".py"
		r.handle(os.path.basename(dest_path)[:-3])
		#TODO: Remove file
	except:
		raise
	
	return
	
