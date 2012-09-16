import cgi
import datetime
import urllib
import webapp2

import jinja2
import os

import json

from google.appengine.ext import db
from google.appengine.api import users


jinja_environment = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Plan(db.Model):
	"""Models an individual Guestbook entry with an author, content, and date."""
	author = db.StringProperty()
	planName = db.StringProperty(multiline=True)
	createTime = db.DateTimeProperty(auto_now_add=True)
	totalTime = db.IntegerProperty()
	spentTime = db.IntegerProperty()

def PlanKey(planName=None):
	"""Constructs a Datastore key for a Plan entity with planName."""
	return db.Key.from_path('Plan', planName or 'defaultPlan')

class MainPage(webapp2.RequestHandler):
	def get(self):
		# it will display all the plan of a user
		user = users.get_current_user()
		if user:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'

		# bug here, it only get a exactly plan with the planName
		planName=self.request.get('planName')
		planQuery = Plan.all().ancestor(PlanKey(planName)).order('-createTime')
		plans = planQuery.fetch(10)

		safePlanName = cgi.escape(planName)
		urlencodePlanName = urllib.urlencode({'planName': planName})
		template_values = {
				'plans': plans,
				'url': url,
				'url_linktext': url_linktext,
				's_PlanName': safePlanName,
				'u_PlanName': urlencodePlanName,
			}
		template = jinja_environment.get_template('/TenThousandHours/index.html')
		self.response.out.write(template.render(template_values))

class MakePlan(webapp2.RequestHandler):
	def post(self):
		# update the plan or make a new plan
		planName = self.request.get("planName");
		if not users.get_current_user() :
			url = users.create_login_url(self.request.uri)
			self.redirect(url)
			return
		else:
			#self.response.out.write("arleady login")
			userName = users.get_current_user().nickname()
			if self.request.get("update") == '1':
				self.response.out.write("update")
			elif self.request.get("newPlan") == '1':
				plan = Plan(parent=PlanKey(planName))
				plan.author = userName
				plan.planName = planName
				plan.totalTime = int( self.request.get("hour") )
				plan.spentTime = 0
				plan.put()
				ret = dict()
				ret['return'] = 1
				self.response.out.write(json.dumps(ret))
			else:
				self.response.out.write("no action")

app = webapp2.WSGIApplication([('/TenThousandHours/', MainPage), 
	('/TenThousandHours/MakePlan', MakePlan)], debug=True)
