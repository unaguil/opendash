# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms.validators import DataRequired
from wtforms import TextField, PasswordField

from model.opendash_model import User

class LoginForm(Form):
	user = TextField(validators=[DataRequired()])
	password = PasswordField(validators=[DataRequired()])

	def __init__(self, session, form=None):
		super(LoginForm, self).__init__(form)
		self.session = session

	def validate(self):
		user = self.get_user()

		if user is None or user.password != self.password.data:
			return False

		return True

	def get_user(self):
		return self.session.query(User).filter_by(user=self.user.data).first()