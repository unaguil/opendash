# -*- coding: utf-8 -*-

from flask import render_template, request
from flask.ext.login import login_required, current_user

from opendash import app, session
from opendash.form.login import LoginForm

@app.route("/user/<userid>")
@login_required
def profile(userid):
	form = LoginForm(session)
	return render_template("profile.html", form=form, user=current_user)