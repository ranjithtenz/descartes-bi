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

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('common.views',
    url(r'^set_language/$', 'set_language', (), name='set_language'),
    url(r'^$', 'home', (), 'home_view'),
    url(r'^about/$', 'about', (), 'about_view'),
    url(r'^backup/$', 'dbbackup', (), 'backup_view'),
    url(r'^restore/$', 'dbrestore', (), 'restore_view'),
)
