# -*- coding: utf-8 -*-

from flask import url_for, request, redirect, render_template
from flask.ext.login import login_user, logout_user, login_required

from opendash import app, session
from opendash.form.login import LoginForm

@app.route("/login", methods=["POST"])
def login():
	form = LoginForm(session, request.form)

	if form.validate_on_submit():
		user = form.get_user()
		login_user(user)

		if user.is_admin():
			return redirect('/admin')
		else:
			return redirect(url_for("edit"))

	return render_template("index.html", form=form, invalid_login=True)

@app.route("/logout", methods=["POST"])
@login_required
def logout():
	logout_user()
	return redirect(request.args.get("next") or url_for("index"))
