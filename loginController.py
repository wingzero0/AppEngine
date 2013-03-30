import cgi
import datetime
import urllib
import webapp2
import logging

from google.appengine.api import users
import json

class LoginController(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        ret = dict()
        homePage = "/TenThousandHours/index.html"
        #ret["selfURI"] = self.request.host_url
        if user:
            url = users.create_logout_url(self.request.host_url + homePage)
            ret['result'] = 1
            ret['userName'] = users.get_current_user().nickname()
            ret["logoutURL"] = url
        else:
            url = users.create_login_url(self.request.host_url + homePage)
            ret['result'] = 0
            ret["loginURL"] = url

        self.response.out.write(json.dumps(ret))
        
app = webapp2.WSGIApplication([('/TenThousandHours/loginController', LoginController)], debug=True)