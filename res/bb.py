from cherrypy.lib import auth_digest

USERS = {'jon': 'secret'}

conf = {
   '/protected/area': {
        'tools.auth_digest.on': True,
        'tools.auth_digest.realm': 'localhost',
        'tools.auth_digest.get_ha1': auth_digest.get_ha1_dict_plain(USERS),
        'tools.auth_digest.key': 'a565c27146791cfb'
   }
}

cherrypy.quickstart(myapp, '/', conf)