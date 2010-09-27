from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import os
import sys
 
class Command(BaseCommand):
    option_list = BaseCommand.option_list + ()
    help = "Starts a Tornado Web."
    args = '[optional port number, or ipaddr:port]'
 
    def handle(self, addrport='', *args, **options):
        import django
        from django.core.handlers.wsgi import WSGIHandler
        from tornado import httpserver, wsgi, ioloop, web
 
	sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
	sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)
 
        if args:
            raise CommandError('Usage: runtornado %s' % self.args)
        if not addrport:
            addr = ''
            port = '8000'
        else:
            try:
                addr, port = addrport.split(':')
            except ValueError:
                addr, port = '', addrport
        if not addr:
            addr = '127.0.0.1'
 
        if not port.isdigit():
            raise CommandError("%r is not a valid port number." % port)
 
        quit_command = (sys.platform == 'win32') and 'CTRL-BREAK' or 'CONTROL-C'
 
        def inner_run():
            from django.conf import settings
            
#            class StaticHandler(web.RequestHandler):
#                def get(self):
#                    self.write("Hello, world")

            #static_settings = {
            #    "static_path":settings.MEDIA_ROOT,
            #    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            #    "login_url": "/login",
            #    "xsrf_cookies": True,
            #}
            #application = tornado.web.Application([
            #    (r"/", MainHandler),
            #    (r"/login", LoginHandler),
            #], **settings)

            #http_server.static_path=settings.MEDIA_ROOT
                        
            
            print "Validating models..."
            self.validate(display_num_errors=True)
            print "\nDjango version %s, using settings %r" % (django.get_version(), settings.SETTINGS_MODULE)
            print "Server is running at http://%s:%s/" % (addr, port)
            print "Quit the server with %s." % quit_command
            django_application = WSGIHandler()
            django_container = wsgi.WSGIContainer(django_application)
            django_server = httpserver.HTTPServer(django_container)
            django_server.listen(int(port), address=addr)

            if 1:
                static_address=addr
                static_port=int(port)+1
                settings.SERVE_STATIC_CONTENT=False
                settings.MEDIA_URL = 'http://%s:%s/static/' % (static_address, static_port)
                settings.ADMIN_MEDIA_PREFIX = settings.MEDIA_URL + 'admin_media/'
                static_application = web.Application([], static_path=settings.MEDIA_ROOT)
                static_server = httpserver.HTTPServer(static_application)
                static_server.listen(static_port, address=addr)
                
            ioloop.IOLoop.instance().start()

        inner_run()

