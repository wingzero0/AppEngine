import cgi
import datetime
import urllib
import webapp2

import jinja2
import os

from google.appengine.ext import db
from google.appengine.api import users


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Greeting(db.Model):
  """Models an individual Guestbook entry with an author, content, and date."""
  author = db.StringProperty()
  content = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)


def guestbook_key(guestbook_name=None):
  """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
  return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')

class MainPage(webapp2.RequestHandler):
    def get(self):
        guestbook_name=self.request.get('guestbook_name')
        greetings_query = Greeting.all().ancestor(
            guestbook_key(guestbook_name)).order('-date')
        greetings = greetings_query.fetch(10)

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        safe_guestbook_name = cgi.escape(guestbook_name)
        urlencode_guestbook_name = urllib.urlencode({'guestbook_name': guestbook_name})
        template_values = {
            'greetings': greetings,
            'url': url,
            'url_linktext': url_linktext,
			's_guestbook_name': safe_guestbook_name,
			'u_guestbook_name': urlencode_guestbook_name,
        }

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))



class Guestbook(webapp2.RequestHandler):
  def post(self):
    # We set the same parent key on the 'Greeting' to ensure each greeting is in
    # the same entity group. Queries across the single entity group will be
    # consistent. However, the write rate to a single entity group should
    # be limited to ~1/second.
    guestbook_name = self.request.get('guestbook_name')
    greeting = Greeting(parent=guestbook_key(guestbook_name))

    if users.get_current_user():
      greeting.author = users.get_current_user().nickname()

    greeting.content = self.request.get('content')
    greeting.put()
    self.redirect('/?' + urllib.urlencode({'guestbook_name': guestbook_name}))


class MyHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>)" % (user.nickname(), users.create_logout_url("/intl/zh-TW/")))
		else:
			greeting = ("<a href=\"%s\">Sign in or register</a>." % users.create_login_url(self.request.uri))

		self.response.out.write("<html><body>%s(redirect uri:%s)</body></html>" % (greeting, self.request.uri))


app = webapp2.WSGIApplication([('/', MainPage), ('/sign', Guestbook),('/user', MyHandler) ], debug=True)

'''
class MainPage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()

		if user:
			self.response.headers['Content-Type'] = 'text/plain'
			self.response.write('Hello, World!' + user.nickname())
		else:
			self.redirect(users.create_login_url(self.request.uri))

app = webapp2.WSGIApplication([('/', MainPage)],
		debug=True)
'''
