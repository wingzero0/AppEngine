import cgi
import datetime
import urllib
import webapp2
import logging

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
	#createTime = db.DateTimeProperty(auto_now_add=True)
	createTime = db.DateTimeProperty()
	totalTime = db.IntegerProperty()
	spentTime = db.IntegerProperty()

def PlanKey(userName=None):
	"""Constructs a Datastore key for a Plan entity with planName."""
	return db.Key.from_path('Plan', userName or 'defaultUser')

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
		postData = self.request.arguments()
		logging.error("start make plan");
		# update the plan or make a new plan
		self.planName = self.request.get("planName");
		logging.error("plan name:" + self.planName);
		if not users.get_current_user() :
			# the javascript will stuck here
			url = users.create_login_url(self.request.uri)
			#self.redirect(url)
			ret = dict()
			ret["result"] = 0
			ret["url"] = url
			self.response.out.write(json.dumps(ret))
			return
		else:
			#self.response.out.write("arleady login")
			self.userName = users.get_current_user().nickname()
			if self.request.get("update") == '1':
				self.response.out.write("update")
			elif self.request.get("newPlan") == '1':
				self.NewPlan()
			else:
				self.response.out.write("no action")

	def NewPlan(self):
		plan = Plan(parent=PlanKey(self.userName))
		plan.author = self.userName
		plan.planName = self.planName
		plan.totalTime = int( self.request.get("hour") )
		plan.spentTime = 0
		plan.createTime = datetime.datetime.now()
		plan.put()
		ret = dict()
		ret['result'] = 1
		ret['createTime'] = plan.createTime.strftime("%Y-%m-%d %H:%M:%S")
		ret['id'] = plan.key().id()
		self.response.out.write(json.dumps(ret))

class GetPlan(webapp2.RequestHandler):
	def get(self):
		# get all user plans
		self.planName = self.request.get("planName");
		if self.request.get("publicPlans") == '1':
			planQuery = Plan.all()
			planQuery = planQuery.order("-createTime")
			plans = planQuery.fetch(10)
			ret = dict()
			ret['result'] = 1
			i = 0
			for plan in plans:
				ret[i] = dict()
				ret[i]['author'] = plan.author
				ret[i]['planName'] = plan.planName
				ret[i]['createTime'] = "%s" % (plan.createTime)
				ret[i]['totalTime'] = plan.totalTime
				ret[i]['spentTime'] = plan.spentTime
				i = i + 1
			self.response.out.write(json.dumps(ret))
			#self.response.out.write(json.dumps(plans))
			
		if not users.get_current_user() :
			# the javascript will stuck here
			url = users.create_login_url(self.request.uri)
			ret = dict()
			ret["result"] = 0
			ret["url"] = url
			self.response.out.write(json.dumps(ret))
			return
		else:
			#self.response.out.write("arleady login")
			self.userName = users.get_current_user().nickname()
			if self.request.get("userPlans") == '1':
				plans = self.GetUserPlans(-1)
				for plan in plans:
					output = "%s<br>" % (plan.createTime)
					self.response.out.write(output)


	def GetUserPlans(self, numberOfPlan):
		planQuery = Plan.all().ancestor(PlanKey(self.userName))
		planQuery = planQuery.order("-createTime")
		plans = planQuery.fetch(10)
		return plans
	
	def GetSpecificPlans(self, author, planName, createTime=None):
		'''
		planQuery = Plan.all().ancestor(PlanKey(self.userName))
		planQuery = planQuery.order("-createTime")
		plans = planQuery.fetch(10)
		'''
		
		

app = webapp2.WSGIApplication([('/TenThousandHours/', MainPage), 
	('/TenThousandHours/MakePlan', MakePlan),
	('/TenThousandHours/GetPlan', GetPlan)], debug=True)
