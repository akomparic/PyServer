__author__ = 'aleksandar'


import re
from cgi import escape


def index(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return ['Missing arguments']


def authentication(environ, start_response):
        args = environ['test.url_args']
        if args:
            subject = escape(args[0])
        else:
            subject = 'Void'
        start_response('200 OK', [('Content-Type', 'text/html')])
        return ['''Auth wait %(subject)s ''' % {'subject': subject}]


def not_found(environ, start_response):
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return ['Not found']

urls = [
    (r'^$', index),
    (r'auth/?', authentication),
    (r'auth/(.+)$', authentication)
]


def main_app(environ, start_response):
    path = environ.get('PATH_INFO', '').lstrip('/')
    for regex, callback in urls:
        match = re.search(regex, path)
        if match is not None:
            environ['test.url_args'] = match.groups()
            return callback(environ, start_response)
    return not_found(environ, start_response)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8080, main_app)
    print('Serving on port 8080...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Cao!')
