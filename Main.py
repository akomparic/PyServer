__author__ = 'aleksandar'


import re


class Selector(object):

    def index(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return ['Missing arguments']

    def authentication(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return ['Authentication temp']

    def not_found(self, environ, start_response):
        start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
        return ['Not found']

    urls = [
        (r'^$', index),
        (r'auth/?', authentication),
        (r'auth/(.+)$', authentication)
    ]

    def main_app(self, environ, start_response):
        path = environ.get('PATH_INFO', '').lstrip('/')
        for regex, callback in self.urls:
            match = re.search(regex, path)
            if match is not None:
                environ['test.url_args'] = match.groups()
                return callback(self, environ, start_response)
        return self.not_found(environ, start_response)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8090, Selector().main_app)
    print('Serving on port 8090...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Cao!')
