from hashlib import md5

def authenticate_digest_app(environ,start_response):
    auth_response = environ.get("HTTP_AUTHORIZATION","none")
    data = getDigestCredentials(auth_response)
    data['method'] = environ.get('REQUEST_METHOD')
    if getDigestResponse(data):
        ret_value = my_digest_app(environ,start_response)
    else:
        ret_value = digestAuthenticationFailed(environ,start_response)
    return ret_value


def getDigestCredentials(auth_response):
    """Parse HTTP authorization string"""
    data = {}
    for item in auth_response.split(','):
        part = item.find("=")
        if part > 0:
            data[item[:part].strip()] = item[part+1:].strip("\"")
    return data


def getDigestResponse(data):
    """Hash local secret"""
    user = data.get("Digest username")
    realm = data.get("realm")
    valueA = md5()
    valueA.update('%s:%s:%s' % (user, realm, 'secret'))
    hashA = valueA.hexdigest()
    #change section on request
    nonce = data.get("nonce")
    uri = data.get("uri")
    method = data.get('method')
    valueB = md5()
    valueB.update("%s:%s" %(method,uri))
    hashB = valueB.hexdigest()

    value = md5()
    value.update("%s:%s:%s" %(hashA, nonce, hashB))

    return data.get("response") == value.hexdigest()


def digestAuthenticationFailed(environ, start_response):
    status = '401 Unauthorized'
    response_headers = [('WWW-Authenticate', 'Digest realm="securearea" nonce="two"'), ('Content-type', 'text/html')]
    start_response(status, response_headers)
    return ["<html><body>Authorization has failed</body></html>"]


def my_digest_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/html')]
    start_response(status, response_headers)
    return ['<html><body><p>Digest stylie.</p></body></html>']


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('192.168.232.1', 8050, authenticate_digest_app)
    print('Serving on port 8050...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Gotov')