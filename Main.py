__author__ = 'aleksandar'


import re


class Selector(object):

    def index(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return ['Missing arguments']

    def authentication(self, environ, start_response):
        while True:
            buf = environ['wsgi.input'].read(4096)
            if len(buf) == 0:
                break
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return ['Goddamn']

    def not_found(self, environ, start_response):
        start_response('404 NOT FOUND', [('Content-Type', 'text/html')])
        return ['Not found']

    urls = [
        (r'^$', index),
        (r'auth/?', authentication),
        (r'auth/(.+)$', authentication)
    ]

    def select(self, environ, start_response):
        path = environ.get('PATH_INFO', '').lstrip('/')
        for regex, callback in self.urls:
            match = re.search(regex, path)
            if match is not None:
                environ['test.url_args'] = match.groups()
                return callback(self, environ, start_response)
        return self.not_found(environ, start_response)


class Auth(object):

    def dummyauthenticator (self, username, password):
        if username == "user" and password == "password":
            return username
        return None

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8060, Selector().select)
    print('Serving on port 8060...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Gotov')
