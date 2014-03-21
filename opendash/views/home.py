# -*- coding: utf-8 -*-

from flask import render_template
from flask.ext.login import current_user

from opendash import app, login_manager, session
from opendash.model.opendash_model import User
from opendash.form.login import LoginForm

# Create user loader function
@login_manager.user_loader
def load_user(user_id):
	user = session.query(User).get(user_id)
	return user

@app.route("/")
def index():
	form = LoginForm(session)

	if current_user.is_authenticated() and current_user.is_admin():
		return redirect('/admin')
	return render_template('index.html', form=form, user=current_user)