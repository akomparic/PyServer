from hashlib import md5
import cherrypy
import random
import string
import re


@cherrypy.expose
def authenticate_digest_app(environ, start_response):
    auth_response = environ.get("HTTP_AUTHORIZATION", "none")
    data = getDigestCredentials(auth_response)
    data['method'] = environ.get('REQUEST_METHOD')
    if getDigestResponse(data):
        ret_value = my_digest_app(environ, start_response)
    else:
        ret_value = digestAuthenticationFailed(environ, start_response)
    return ret_value


def getDigestCredentials(auth_response):
    """Parse HTTP authorization string"""
    data = {}
    for item in auth_response.split(','):
        part = item.find("=")
        if part > 0:
            data[item[:part].strip()] = item[part+1:].strip("\"")
    return data

nonce = ''.join([random.choice(string.ascii_lowercase + string.digits) for n in xrange(34)])

def getDigestResponse(data):
    """Hash local secret"""
    f = open('ident')
    fil = f.read()
    au = re.search(r'username=\w+', fil)
    ap = re.search(r'password=\w+', fil)
    autemp = au.group(0)
    ausername = autemp[9:]
    aptemp = ap.group(0)
    apassword = aptemp[9:]
    valueA = md5()
    valueA.update('%s:%s:%s' % (ausername, "str@host.com", apassword))
    hashA = valueA.hexdigest()
    print('HA1 ' + hashA)

    #change section on request
    uri = '/digest/'
    method = 'PUT'
    valueB = md5()
    valueB.update("%s:%s" % (method, uri))
    hashB = valueB.hexdigest()
    print('HA2 ' + hashB)
    nt = nonce
    print('nonce ' + nt)
    value = md5()
    value.update("%s:%s:%s" % (hashA, nt, hashB))
    print('res ' + value.hexdigest())

    return data.get("response") == value.hexdigest()


def digestAuthenticationFailed(environ, start_response):
    status = '401 Unauthorized'
    response_headers = [('WWW-Authenticate', 'Digest realm="str@host.com" nonce=' + nonce), ('Content-type', 'text/html')]
    start_response(status, response_headers)
    return ["<html><body>Authorization has failed</body></html>"]


def my_digest_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/html')]
    start_response(status, response_headers)
    return ['<html><body><p>Digest stylie.</p></body></html>']


if __name__ == '__main__':
    cherrypy.tree.graft(authenticate_digest_app, "/digest/")
    cherrypy.server.unsubscribe()
    server = cherrypy._cpserver.Server()
    server.socket_host = "192.168.232.1"
    server.socket_port = 8050
    server.thread_pool = 30
    server.subscribe()

    cherrypy.engine.start()
    cherrypy.engine.block()

#if __name__ == '__main__':
#    from wsgiref.simple_server import make_server
#    httpd = make_server('192.168.232.1', 8050, authenticate_digest_app)
#    print('Serving on port 8050...')
#    try:
#        httpd.serve_forever()
#    except KeyboardInterrupt:
#        print('Gotov')