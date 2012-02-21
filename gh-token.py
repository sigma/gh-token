from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.urlfetch import fetch

import os
import ConfigParser
import urlparse

client_id = None
client_secret = None
scope = "user,repo,gist"
gh_url = "https://github.com/login/oauth/"

class MainPage(webapp.RequestHandler):
    def get(self):
        self.redirect((gh_url + "authorize?client_id=%s&scope=%s")
                      % (client_id, scope))

class AuthPage(webapp.RequestHandler):
    def get(self):
        code = self.request.get('code')
        resp = fetch((gh_url + "access_token?client_id=%s&client_secret=%s&code=%s")
                     % (client_id, client_secret, code),
                     method="POST")

        qs = dict([t.split("=") for t in resp.content.split("&")])
        access_token = qs['access_token']

        template_values = {
            'access_token': access_token,
        }

        path = os.path.join(os.path.dirname(__file__), 'oauth.html')
        self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication([('/', MainPage),
                                      ('/oauth', AuthPage)],
                                     debug=False)

def main():
    parser = ConfigParser.ConfigParser()
    parser.read('settings.ini')

    try:
        global client_id
        client_id = parser.get('main', 'client_id')

        global client_secret
        client_secret = parser.get('main', 'client_secret')

    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
        # no settings
        pass
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

