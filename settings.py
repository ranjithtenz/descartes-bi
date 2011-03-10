# Django project settings.
# FLAGS
import os
import sys 

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "./"))
sys.path.append(os.path.join(PROJECT_ROOT, 'modules'))
sys.path.append(os.path.join(PROJECT_ROOT, 'apps'))
sys.path.append(os.path.join(PROJECT_ROOT, 'customization_apps'))
sys.path.append(os.path.join(PROJECT_ROOT, 'shared_apps'))
sys.path.append(os.path.join(PROJECT_ROOT, '3rd_party_apps'))


PROJECT_NAME = 'descartes'
PROJECT_TITLE = 'Descartes'

#DEBUG = False
#TEMPLATE_DEBUG = DEBUG
#DEBUG_APPS_DJANGO_EXTENSIONS = False
#DEVELOPMENT = False
#SERVE_STATIC_CONTENT = True

DEBUG = False
DEVELOPMENT = False
TEMPLATE_DEBUG = True


ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(PROJECT_ROOT, '%s.sqlite' % PROJECT_NAME),     # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

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

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'site_media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/%s-site_media/' % PROJECT_NAME

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = MEDIA_URL + 'grappelli/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '@mff4*!u6*nc5+0pmkvcu#$&n1mq=n=+mb6g%2!ivyj3_m_g-1'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
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
    os.path.join(PROJECT_ROOT, 'branding'),
    os.path.join(PROJECT_ROOT, 'templates'),
)

INSTALLED_APPS = (
    'grappelli',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.humanize',
    'reports',
    'common',
)

       
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
#    'grappelli.context_processors.admin_template_path',
)
#===== Configuration options ===============
#--------- Grappelli ----------------
#GRAPPELLI_ADMIN_TITLE = PROJECT_TITLE
GRAPPELLI_ADMIN_TITLE = PROJECT_TITLE
#--------- Django -------------------
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
#------------------------------------
SOURCE_DATABASE_ENGINE = 'sqlite3'          # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
SOURCE_DATABASE_NAME = PROJECT_NAME + '.sqlite'        # Or path to database file if using sqlite3.
SOURCE_DATABASE_USER = ''                       # Not used with sqlite3.
SOURCE_DATABASE_PASSWORD = ''                   # Not used with sqlite3.
SOURCE_DATABASE_HOST = ''                       # Set to empty string for localhost. Not used with sqlite3.
SOURCE_DATABASE_PORT = ''    

try:
    from settings_local import *
except ImportError:
    pass

if DEVELOPMENT:
    INTERNAL_IPS = ('127.0.0.1',)

    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )
    try:
        import rosetta
        INSTALLED_APPS += ('rosetta',)
    except ImportError:
        #print 'rosetta is not installed'
        pass

    try:
        import django_extensions
        INSTALLED_APPS +=('django_extensions',)
    except ImportError:
        #print 'django_extensions is not installed'
        pass

    try:
        import debug_toolbar
        #INSTALLED_APPS.append('debug_toolbar')
    except ImportError:
        #print 'debug_toolbar is not installed'
        pass

    TEMPLATE_CONTEXT_PROCESSORS += ('django.core.context_processors.debug',)

    WSGI_AUTO_RELOAD = True
    if 'debug_toolbar' in INSTALLED_APPS:
        MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware')
        DEBUG_TOOLBAR_CONFIG={
            'INTERCEPT_REDIRECTS' : False,
        }
