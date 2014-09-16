from hashlib import md5
import cherrypy
import random
import string
import re
import json


class Server(object):
    @cherrypy.expose
    def indexapp(self,environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'text/html')]
        start_response(status, response_headers)
        return ["<html><body>Index of the SecureTextWriter server.</body></html>"]

    @cherrypy.expose
    def authenticate_digest_app(self, environ, start_response):
        auth_response = environ.get("HTTP_AUTHORIZATION", "none")
        data = self.getDigestCredentials(auth_response)
        data['method'] = environ.get('REQUEST_METHOD')
        if self.getDigestResponse(data):
            ret_value = self.my_digest_app(environ, start_response)
        else:
            ret_value = self.digestAuthenticationFailed(environ, start_response)
        return ret_value

    def getDigestCredentials(self, auth_response):
        """Parse HTTP authorization string"""
        data = {}
        for item in auth_response.split(','):
            part = item.find("=")
            if part > 0:
                data[item[:part].strip()] = item[part+1:].strip("\"")
        return data

    def getDigestResponse(self, data):
        """Hash local secret"""
        user = data.get("Digest username")
        if user is None:
            return False
        else:
            f = open('ident')
            fil = f.read()
            au = re.search(re.compile('username=%s' %user), fil)
            autemp = au.group(0)
            ausername = autemp[9:]
            if not ausername == user:
                return False
            else:
                pass1temp = re.search(re.compile('username=%s:password=\w+' %user), fil)
                pass1string = pass1temp.group(0)
                pass2temp = re.search(r'password=\w+', pass1string)
                pass2string = pass2temp.group(0)
                apassword = pass2string[9:]
                valueA = md5()
                valueA.update('%s:%s:%s' % (user, 'str@host.com', apassword))
                hashA = valueA.hexdigest()

                #change section on request
                uri = '/digest/'
                method = 'PUT'
                valueB = md5()
                valueB.update("%s:%s" % (method, uri))
                hashB = valueB.hexdigest()
                nt = self.nonce
                value = md5()
                value.update("%s:%s:%s" % (hashA, nt, hashB))

                return data.get("response") == value.hexdigest()

    def digestAuthenticationFailed(self, environ, start_response):
        status = '401 Unauthorized'
        self.nonce = ''.join([random.choice(string.ascii_lowercase + string.digits) for n in xrange(34)])
        response_headers = [('WWW-Authenticate', 'Digest realm="str@host.com" nonce=' + self.nonce), ('Content-type', 'text/html')]
        start_response(status, response_headers)
        return ["<html><body>Authorization has failed</body></html>"]

    def my_digest_app(self, environ, start_response):
        import os
        from time import strftime

        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            request_body_size = 0

        request_body = environ['wsgi.input'].read(request_body_size)
        jdata = json.loads(request_body)
        text = jdata['content']
        tstamp = strftime("%d%m%y%H%M%S")
        path = 'res'
        if not os.path.exists(path):
            os.makedirs(path)
        filename = 'Transfer_' + tstamp
        with open(os.path.join(path, filename), 'wb') as temp_file:
            temp_file.write(text)

        self.nonce = ''.join([random.choice(string.ascii_lowercase + string.digits) for n in xrange(34)])
        status = '200 OK'
        response_headers = [('Content-type', 'text/html')]
        start_response(status, response_headers)
        return ['<html><body><p>File written.</p></body></html>']


if __name__ == '__main__':
    cherrypy.tree.graft(Server().indexapp, "/")
    cherrypy.tree.graft(Server().authenticate_digest_app, "/digest/")
    cherrypy.server.unsubscribe()
    server = cherrypy._cpserver.Server()
    server.socket_host = "192.168.232.1"
    server.socket_port = 8050
    server.thread_pool = 30
    server.subscribe()

    cherrypy.engine.start()
    cherrypy.engine.block()