import re


class Selector(object):

    def index(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return ['Missing arguments']

    def authentication(self, environ, start_response):
        buf = environ['wsgi.input'].read(int(environ['CONTENT_LENGTH']))
        u = re.search(r'username:\w+', buf)
        p = re.search(r'password:\w+', buf)
        utemp = u.group(0)
        username = utemp[9:]
        ptemp = p.group(0)
        password = ptemp[9:]
        Auth().dummyauthenticator(username, password)

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

    def dummyauthenticator(self, username, password):
        f = open('authen')
        fil = f.read()
        au = re.search(r'username=\w+', fil)
        ap = re.search(r'password=\w+', fil)
        autemp = au.group(0)
        ausername = autemp[9:]
        aptemp = ap.group(0)
        apassword = aptemp[9:]
        if username == ausername and password == apassword:
            print('Auth good')
        return None


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8050, Selector().select)
    print('Serving on port 8050...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Gotov')