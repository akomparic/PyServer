import re
import json


class Function(object):
    def index(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return ['Missing arguments']

    def authentication(self, environ, start_response):
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            request_body_size = 0
        request_body = environ['wsgi.input'].read(request_body_size)
        data = json.loads(request_body)
        username = data['user']
        password = data['pass']
        f = open('ident')
        fil = f.read()
        au = re.search(r'username=\w+', fil)
        ap = re.search(r'password=\w+', fil)
        autemp = au.group(0)
        ausername = autemp[9:]
        aptemp = ap.group(0)
        apassword = aptemp[9:]
        if username == ausername and password == apassword:
            text = data['content']
            return self.writer(start_response, text)
        return self.badlogin(start_response)

    def not_found(self, environ, start_response):
        start_response('404 NOT FOUND', [('Content-Type', 'text/html')])
        return ['Not found']

    def badlogin(self, start_response):
        start_response('403 FORBIDDEN', [('Content-Type', 'text/html')])
        return ['Bad login']

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

    def writer(self, start_response, text):
        import os
        from time import strftime
        tstamp = strftime("%d%m%y%H%M%S")
        path = 'res'
        if not os.path.exists(path):
            os.makedirs(path)
        filename = 'Transfer_' + tstamp
        with open(os.path.join(path, filename), 'wb') as temp_file:
            temp_file.write(text)
        start_response('200 OK', [('Content-Type', 'text/html')])
        return ['File Saved']


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('192.168.232.1', 8050, Function().select)
    print('Serving on port 8050...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Gotov')