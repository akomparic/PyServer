import re


class Function(object):

    def index(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return ['Missing arguments']

    def authentication(self, environ, start_response):
        buf = environ['wsgi.input'].read(int(environ['CONTENT_LENGTH']))
        u = re.search(r'username:\w+', buf)
        p = re.search(r'password:\w+', buf)
        t = re.search(r'<h3>.*</h3>', buf)
        utemp = u.group(0)
        username = utemp[9:]
        ptemp = p.group(0)
        password = ptemp[9:]
        textemp = t.group(0)
        text = textemp[4:-5]
        f = open('ident')
        fil = f.read()
        au = re.search(r'username=\w+', fil)
        ap = re.search(r'password=\w+', fil)
        autemp = au.group(0)
        ausername = autemp[9:]
        aptemp = ap.group(0)
        apassword = aptemp[9:]
        if username == ausername and password == apassword:
            print ['test ' + text]
            return self.filewriter(text, start_response)
        return False

    def filewriter(self, text, start_response):
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
        return ['Text Saved']

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


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8050, Function().select)
    print('Serving on port 8050...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Gotov')