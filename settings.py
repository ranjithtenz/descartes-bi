# Django project settings.
# FLAGS

PROJECT_TITLE = 'Descartes'

DEBUG = False
TEMPLATE_DEBUG = DEBUG
DEBUG_APPS_DJANGO_EXTENSIONS = False
DEVELOPMENT = False
SERVE_STATIC_CONTENT = False

import os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "./"))

import sys 
sys.path.append(os.path.join(PROJECT_ROOT, 'modules'))
sys.path.append(os.path.join(PROJECT_ROOT, 'apps'))
sys.path.append(os.path.join(PROJECT_ROOT, 'customization_apps'))
sys.path.append(os.path.join(PROJECT_ROOT, 'shared_apps'))
sys.path.append(os.path.join(PROJECT_ROOT, '3rd_party_apps'))

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'             # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = PROJECT_TITLE + '.sqlite'       # Or path to database file if using sqlite3.
DATABASE_USER = ''                      # Not used with sqlite3.
DATABASE_PASSWORD = ''                  # Not used with sqlite3.
DATABASE_HOST = ''                      # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''                      # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Puerto_Rico'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
#LANGUAGE_CODE = 'en-us'

LANGUAGE_CODE = 'es'

ugettext = lambda s: s

LANGUAGES = (
    ('es', ugettext('Spanish')),
    ('en', ugettext('English')),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
#MEDIA_ROOT = 'site_media/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'site_media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/site_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".

#ADMIN_MEDIA_PREFIX = '/media/'
#ADMIN_MEDIA_PREFIX = '/admin_media/'
ADMIN_MEDIA_PREFIX = MEDIA_URL + 'admin_media/'


# Make this unique, and don't share it with anybody.
SECRET_KEY = '@mff4*!u6*nc5+0pmkvcu#$&n1mq=n=+mb6g%2!ivyj3_m_g-1'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
#   './branding',
    os.path.join(PROJECT_ROOT, 'branding'),
#   './templates',
    os.path.join(PROJECT_ROOT, 'templates'),

)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
#    'django.contrib.sites',
    'django.contrib.admin',
    'reports',
    'wsgi',
    'grappelli',
    'common',
    'django.contrib.humanize',
    'tornado_app',
)

CUSTOMIZATION_APPS = ()

if DEVELOPMENT:
    try:
        import django_extensions
        INSTALLED_APPS += ('django_extensions',)
    except ImportError:
        pass

    try:
        import rosetta
        INSTALLED_APPS += ('rosetta',)
    except ImportError:
        pass
        
try:
    import ldap_groups
    import ldap
    INSTALLED_APPS += ('ldap_groups',)
except ImportError:
    pass

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    'django.core.context_processors.request',
)

LOGIN_URL = '/login/'

GRAPPELLI_ADMIN_TITLE = PROJECT_TITLE

SOURCE_DATABASE_ENGINE = 'sqlite3'          # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
SOURCE_DATABASE_NAME = PROJECT_TITLE + '.sqlite'        # Or path to database file if using sqlite3.
SOURCE_DATABASE_USER = ''                       # Not used with sqlite3.
SOURCE_DATABASE_PASSWORD = ''                   # Not used with sqlite3.
SOURCE_DATABASE_HOST = ''                       # Set to empty string for localhost. Not used with sqlite3.
SOURCE_DATABASE_PORT = ''    

try:
    from settings_local import *
    try:
        INSTALLED_APPS += CUSTOMIZATION_APPS
    except:
        pass
except ImportError:
    pass
    #print u"No file 'settings_local.py' found."
    
