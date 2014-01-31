# -*- coding: utf-8 -*-

from flask import jsonify, request, render_template, url_for, redirect, abort
from flask.ext.login import login_required, current_user

import rdflib

from opendash import app, session
from opendash.form.login import LoginForm

from opendash.model.opendash_model import Endpoint, Report, Chart

DATA_TYPE = 'data_type'
OBJECT_TYPE = 'object_type'

def has_privileges(report):
	return not current_user.is_anonymous() and report.user == current_user.id	

@app.route("/report/<report_id>/edit")
@login_required
def report_edit(report_id):
	form = LoginForm(session)

	report = session.query(Report).filter_by(id=report_id).first()

	if not has_privileges(report):
		return abort(401)

	return render_template('report_edit.html', form=form, user=current_user, report=report, edit=True)

@app.route("/report/<report_id>")
def report_view(report_id):
	form = LoginForm(session)

	report = session.query(Report).filter_by(id=report_id).first()

	if report.public:
		return render_template('report_edit.html', form=form, user=current_user, report=report, edit=False)
	elif has_privileges(report):
		 return redirect(url_for('report_edit', report_id=report_id))
	else:
		return abort(404)

@app.route("/report/<report_id>/chart/new")
@login_required
def new_chart(report_id):
	report = session.query(Report).filter_by(id=report_id).first()

	if not has_privileges(report):
		return abort(401)

	chart = Chart()
	report.charts.append(chart)
	session.commit()

	form = LoginForm(session)
	return render_template('edit.html', form=form, user=current_user, report=report, chart=chart, new=True)

@app.route("/report/<report_id>/chart/<chart_id>/delete", methods=['POST'])
@login_required
def delete_chart(report_id, chart_id):
	report = session.query(Report).filter_by(id=report_id).first()

	if not has_privileges(report):
		return abort(401)

	session.query(Chart).filter_by(id=chart_id, report=report_id).delete()
	session.commit()

	return jsonify(data=None)

@app.route("/report/<report_id>/chart/edit")
@login_required
def chart_edit(report_id):
	report = session.query(Report).filter_by(id=report_id).first()

	if not has_privileges(report):
		return abort(401)

	form = LoginForm(session)
	return render_template('edit.html', form=form, user=current_user)

@app.route("/report/<report_id>/chart/<chart_id>/save", methods=['POST'])
@login_required
def chart_save(report_id, chart_id):
	report = session.query(Report).filter_by(id=report_id).first()

	if not has_privileges(report):
		return abort(401)
	
	json = request.form['chart']

	chart = session.query(Chart).filter_by(id=chart_id).first()
	chart.json = json

	session.commit()	

	report = session.query(Report).filter_by(id=chart.report).first()

	return redirect(url_for("report_edit", report_id=report.id))