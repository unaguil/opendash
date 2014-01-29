# -*- coding: utf-8 -*-

from flask import jsonify, request, render_template
from flask.ext.login import login_required, current_user

import rdflib

from opendash import app, session
from opendash.form.login import LoginForm

from opendash.model.opendash_model import Endpoint

DATA_TYPE = 'data_type'
OBJECT_TYPE = 'object_type'

@app.route("/report/<report_id>/edit")
@login_required
def report_edit(report_id):
	form = LoginForm(session)
	return render_template('report_edit.html', form=form, user=current_user)
