# -*- coding: utf-8 -*-

from flask import redirect, url_for

from flask.ext.admin import BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.login import current_user, logout_user

from model.opendash_model import User, Endpoint

from flask import request

class UserView(ModelView):

	def __init__(self, session, **kwargs):
		super(UserView, self).__init__(User, session, **kwargs)

	def is_accessible(self):
		return current_user.is_authenticated() and current_user.is_admin()

class EndpointView(ModelView):

	def __init__(self, session, **kwargs):
		super(EndpointView, self).__init__(Endpoint, session, **kwargs)

	def is_accessible(self):
		return current_user.is_authenticated() and current_user.is_admin()

class LogoutView(BaseView):

	@expose('/')
	def index(self):
		logout_user()
		return redirect(request.args.get("next") or url_for("index"))