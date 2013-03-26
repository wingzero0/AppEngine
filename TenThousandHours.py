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
	googleID = db.StringProperty()
	planName = db.StringProperty(multiline=True)
	#createTime = db.DateTimeProperty(auto_now_add=True)
	createTime = db.DateTimeProperty()
	totalTime = db.IntegerProperty()
	spentTime = db.IntegerProperty()

#def PlanKey(userName=None):
#	"""Constructs a Datastore key for a Plan entity with planName."""
#	return db.Key.from_path('Plan', userName or 'defaultUser')

def PlanKey(userID=None):
	"""Constructs a Datastore key for a Plan entity with planName."""
	return db.Key.from_path('Plan', userID or 'defaultUser')

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
		#postData = self.request.arguments()
		logging.error("start make plan");
		ret = dict()
		# update the plans or make a new plan
		if not users.get_current_user() :
			# the javascript will stuck here
			url = users.create_login_url(self.request.uri)
			#self.redirect(url)
			ret["result"] = 0
			ret["url"] = url
			self.response.out.write(json.dumps(ret))
			return
		else:
			self.userName = users.get_current_user().nickname()
			self.userID = users.get_current_user().user_id()
			if self.request.get("op") == 'update':
				self.UpdatePlans()
			elif self.request.get("op") == 'newPlan':
				self.planName = self.request.get("planName");
				logging.error("plan name:" + self.planName);
				self.NewPlan()
			else:
				ret["errorMessage"] = "no action:op=%s" % (self.request.get("op"))
				self.response.out.write(json.dumps(ret))

	def NewPlan(self):
		plan = Plan(parent=PlanKey(self.userID))
		plan.author = self.userName
		plan.googleID = self.userID
		plan.planName = self.planName
		plan.totalTime = int( self.request.get("totalTime") )
		plan.spentTime = 0
		plan.createTime = datetime.datetime.now()
		plan.put()
		ret = dict()
		ret['result'] = 1
		ret['createTime'] = plan.createTime.strftime("%Y-%m-%d %H:%M:%S")
		ret['id'] = plan.key().id()
		self.response.out.write(json.dumps(ret))
	
	def UpdatePlans(self):
		num = int ( self.request.get("num") )
		ret = dict()
		flag = 1
		for i in range(num):
			# from 0 to num -1
			index = "%d" % (i) 
			planTuple = self.request.get("id" + index).partition(u"plan")
			planID = int(planTuple[2])
			spentTime = int(self.request.get("spentTime" + index))
			flag = flag & self.UpdatePlan(planID, 0, spentTime, "Tmp")
			if flag == 0:
				ret['result'] = 0
				ret['errorMessage'] = "put fail"
				ret['id'] = planID
				self.response.out.write(json.dumps(ret))
				return
		
		ret["result"] = 1
		self.response.out.write(json.dumps(ret))
			
	def UpdatePlan(self, planID, totalTime, spentTime, planName):
		plan = Plan.get_by_id(planID, PlanKey(self.userID))
		
		if plan:
			#plan.planName = self.planName
			#plan.totalTime = totalTime
			plan.spentTime = spentTime
			plan.put()
			return 1 
		else:
			return 0
	'''
	def UpdatePlan(self):
		plan = Plan.get_by_id(int(self.request.get("id")), PlanKey(self.userID))
		
		if plan:
			#if (plan.author)
			plan.planName = self.planName
			plan.totalTime = int( self.request.get("totalTime") )
			plan.spentTime = int( self.request.get("spentTime") )
			plan.put()
			ret = dict()
			ret['result'] = 1
			ret['id'] = plan.key().id()
			self.response.out.write(json.dumps(ret)) 
		else:
			ret = dict()
			ret['result'] = 0
			ret['id'] = int (self.request.get("id")) 
			self.response.out.write(json.dumps(ret))
	'''
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
			
		if not users.get_current_user() :
			# the javascript will stuck here
			url = users.create_login_url(self.request.uri)
			ret = dict()
			ret["result"] = 0
			ret["url"] = url
			self.response.out.write(json.dumps(ret))
			return
		else:
			self.userName = users.get_current_user().nickname()
			self.userID = users.get_current_user().user_id()
			if self.request.get("op") == "userPlans":
				plans = self.GetUserPlans(-1)
				self.OutputPlans(plans)

	def GetUserPlans(self, numberOfPlan):
		planQuery = Plan.all().ancestor(PlanKey(self.userID))
		planQuery = planQuery.order("-createTime")
		plans = planQuery.fetch(10)
		return plans
	
	def GetSpecificPlans(self, author, planName, createTime=None):
		'''
		planQuery = Plan.all().ancestor(PlanKey(self.userName))
		planQuery = planQuery.order("-createTime")
		plans = planQuery.fetch(10)
		'''
		
	def OutputPlans(self, plans):
		ret = dict()
		ret['result'] = 1
		ret["plans"] = dict()
		i = 0
		for plan in plans:
			ret["plans"][i] = dict()
			ret["plans"][i]['author'] = plan.author
			ret["plans"][i]['id'] = plan.key().id()
			ret["plans"][i]['planName'] = plan.planName
			ret["plans"][i]['createTime'] = plan.createTime.strftime("%Y-%m-%d %H:%M:%S")
			ret["plans"][i]['totalTime'] = plan.totalTime
			ret["plans"][i]['spentTime'] = plan.spentTime
			i = i + 1
		ret["totalNum"] = i
		self.response.out.write(json.dumps(ret))
		
class Test(webapp2.RequestHandler):
	def get(self):
		#run time Test
		self.userName = users.get_current_user().nickname()
		planQuery = Plan.all().ancestor(PlanKey(self.userName))
		planQuery = planQuery.order("-createTime")
		plans = planQuery.fetch(10)
		str = ""
		for plan in plans:
			str = str + plan.planName
		ret = dict()
		ret["ret"]= str
		self.response.out.write(json.dumps(ret))


app = webapp2.WSGIApplication([('/TenThousandHours/', MainPage), 
	('/TenThousandHours/MakePlan', MakePlan),
	('/TenThousandHours/GetPlan', GetPlan),
	('/TenThousandHours/Test', Test)], debug=True)
