# -*- coding: utf-8 -*-

from flask import render_template, request, redirect, url_for
from flask.ext.login import login_required, current_user

from opendash import app, session
from opendash.form.login import LoginForm

from opendash.model.opendash_model import Report

@app.route("/user/profile")
@login_required
def profile():
	form = LoginForm(session)

	return render_template("profile.html", form=form, user=current_user, reports=current_user.reports)

@app.route("/report/<report_id>/make_public")
@login_required
def make_public(report_id):
	report = session.query(Report).filter_by(id=report_id, user=current_user.id).first()

	if report is not None:
		report.public = True

	session.commit()

	return redirect(url_for("profile"))

@app.route("/report/<report_id>/make_private")
@login_required
def make_private(report_id):
	report = session.query(Report).filter_by(id=report_id, user=current_user.id).first()

	if report is not None:
		report.public = False

	session.commit()

	return redirect(url_for("profile"))

@app.route("/report/<report_id>/remove")
@login_required
def remove_report(report_id):
	report = session.query(Report).filter_by(id=report_id, user=current_user.id).first()

	session.delete(report)

	session.commit()

	return redirect(url_for("profile"))