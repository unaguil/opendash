# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect, url_for
from flask import jsonify, request
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.login import LoginManager, login_user, current_user, logout_user, login_required
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, ValidationError
from wtforms.validators import DataRequired

import rdflib
import json
import random

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from model.opendash_model import User, Endpoint

app = Flask(__name__)

engine = create_engine('sqlite:///opendash.db')
Session = sessionmaker(bind=engine)
session = Session()

app.config['SECRET_KEY'] = '123456790'

login_manager = LoginManager()
login_manager.setup_app(app)

# Create user loader function
@login_manager.user_loader
def load_user(user_id):
	user = session.query(User).get(user_id)
	return user

@app.route("/")
def index():
	form = LoginForm()

	if current_user.is_authenticated() and current_user.is_admin():
		return redirect('/admin')
	return render_template('index.html', form=form, user=current_user)

@app.route("/report")
@login_required
def report():
	form = LoginForm()
	return render_template('report.html', form=form, user=current_user)

@app.route("/endpoints")
@login_required
def get_endpoints():
	available_endpoints = session.query(Endpoint).all()

	endpoints = []
	for endpoint in available_endpoints:
		endpoints.append({'id': endpoint.id, 'url': endpoint.url })

	return jsonify(endpoints=endpoints)

@app.route("/endpoints/get_graphs", methods=['POST'])
@login_required
def get_endpoint_graphs():
	endpoint = request.form['endpoint']

	g = rdflib.ConjunctiveGraph('SPARQLStore')
	g.open(endpoint)

	qres = g.query("select distinct ?g where { graph ?g {?s ?p ?o} }")

	graphs = []
	for index, graph in enumerate(qres):
		graphs.append({'id': index, 'name': graph[0]})

	return jsonify(graphs=graphs)


def loadIgnoredPrefixes():
	ignored = []
	with open('ignored.txt') as f:
		ignored = f.read().splitlines()

	return ignored

def getFilter(var):
	ignored = loadIgnoredPrefixes()	

	filter = ''
	if len(ignored) > 0:
		filter += "FILTER ("

		first = True
		for prefix in ignored:
			if first:
				filter += " !regex(str(%s), \"%s\")" % (var, prefix)
				first = False
			else:
				filter += " && !regex(str(%s), \"%s\")" % (var, prefix)
		filter += ")"

	return filter

def get_properties(g, graph, clazz):
	query = """SELECT DISTINCT ?property (COUNT(DISTINCT ?s) AS ?count)
				FROM <%s>
				WHERE 	{ 	?s a <%s> . 
							?s ?property ?o . 
							%s 
						} GROUP BY ?property ORDER BY desc(?count) LIMIT 25"""
	
	query =  query % (graph, clazz, getFilter("?property"))
	qres = g.query(query)

	properties = []
	for p in qres:
		property = {
				'uri': str(p[0]),
				'datatype': get_property_type(g, graph, clazz, str(p[0]))
			}

		properties.append(property)

	return properties

def infer_datatype(value):
	if type(value) is str:
		return 'http://www.w3.org/2001/XMLSchema#string'
	elif type(value) is int:
		return 'http://www.w3.org/2001/XMLSchema#integer'
	return ''

def get_property_type(g, graph, clazz, property):
	query = """SELECT ?value FROM <%s> WHERE {
				?s a <%s> .
				?s <%s> ?value .
				} LIMIT 1"""

	query = query % (graph, clazz, property)

	qres = g.query(query)
	for value in qres:
		if type(value[0]) is rdflib.term.Literal:
			if value[0].datatype is not '':
				return str(value[0].datatype)

		return infer_datatype(str(value[0]))

def get_description(endpoint, graph):
	g = rdflib.ConjunctiveGraph('SPARQLStore')
	g.open(endpoint)

	query = "SELECT DISTINCT ?class FROM <%s> WHERE { [] a ?class " + getFilter("?class") + " } LIMIT 50"
	query = query % graph

	qres = g.query(query)

	desc = {}
	desc['endpoint'] = endpoint
	desc['graph'] = graph

	classes = []
	for c in qres:
		clazz = {}
		clazz['classURI'] = str(c[0])

		clazz['properties'] = get_properties(g, graph, str(c[0]))
		classes.append(clazz)

	desc['classes'] = classes

	return desc

@app.route("/endpoints/get_description", methods=['POST'])
@login_required
def get_source_description():
	endpoint = request.form['endpoint']
	graph = request.form['graph']

	desc = get_description(endpoint, graph)

	return jsonify(desc=desc)

def get_class_properties(clazz, desc):
	for c in desc['classes']:
		if c['classURI'] == clazz:
			return c['properties']
	return []

def get_connections(clazz, desc):
	connections = []

	for c in desc['classes']:
		if c['classURI'] != clazz:
			for p1 in c['properties']:
				properties = []
				for p2 in get_class_properties(clazz, desc):
					if p1['uri'] == p2['uri']:
						p1['connection'] = p2['uri']
						properties.append(p1)

				if len(properties) > 0:
					connections.append({'classURI' : c['classURI'], 'properties': properties})

	return connections

@app.route("/endpoints/get_connections", methods=['POST'])
@login_required
def get_compatible_classes():
	endpoint = request.form['endpoint']
	graph = request.form['graph']
	clazz = request.form['class']

	desc = get_description(endpoint, graph)

	connections = get_connections(clazz, desc)

	return jsonify(connections=connections)

@app.route("/endpoints/get_data", methods=['POST'])
@login_required
def get_data():
	endpoint = request.form['endpoint']
	graph = request.form['graph']
	mainclass = request.form['mainclass']
	xvalues = request.form['xvalues']
	yvalues = request.form['yvalues']

	g = rdflib.ConjunctiveGraph('SPARQLStore')
	g.open(endpoint)

	query = """SELECT ?x ?y FROM <%s> WHERE {
				?s a <%s> .
				?s <%s> ?x .
				?s <%s> ?y .
				} ORDER BY(?x)"""

	query = query % (graph, mainclass, xvalues, yvalues)
	qres = g.query(query)

	data = []
	for row in qres:
		data.append({'x' : str(row[0]), 'y': str(row[1])})

	return jsonify(data=data)

@app.route("/endpoints/get_class_data", methods=['POST'])
@login_required
def get_class_data():
	endpoint = request.form['endpoint']
	graph = request.form['graph']
	mainclass = request.form['mainclass']
	xvalues = request.form['xvalues']
	secondary_class = request.form['secondaryclass']
	yvalues = request.form['yvalues']
	connection = request.form['connection']

	g = rdflib.ConjunctiveGraph('SPARQLStore')
	g.open(endpoint)

	query = """SELECT ?x ?y FROM <%s> WHERE {
				?s1 a <%s> .
				?s2 a <%s> .
				?s1 <%s> ?x .
				?s2 <%s> ?y .
				?s1 <%s> ?v1 .
				?s2 <%s> ?v2 .
				FILTER (?v1 = ?v2) 
				} ORDER BY(?x)"""

	query = query % (graph, mainclass, secondary_class, xvalues, yvalues, connection, connection)

	qres = g.query(query)

	data = []
	for row in qres:
		data.append({'x' : str(row[0]), 'y': str(row[1])})

	return jsonify(data=data)

@app.route("/login", methods=["POST"])
def login():
	form = LoginForm(request.form)

	if form.validate_on_submit():
		user = form.get_user()
		login_user(user)

		if user.is_admin():
			return redirect('/admin')
		else:
			return redirect(url_for("report"))

	return render_template("index.html", form=form, invalid_login=True)

@app.route("/logout", methods=["POST"])
@login_required
def logout():
	logout_user()
	form = LoginForm(request.form)
	return redirect(request.args.get("next") or url_for("index"))

class LoginForm(Form):
	user = TextField(validators=[DataRequired()])
	password = PasswordField(validators=[DataRequired()])

	def validate(self):
		user = self.get_user()

		if user is None or user.password != self.password.data:
			return False

		return True

	def get_user(self):
		return session.query(User).filter_by(user=self.user.data).first()

class UserView(ModelView):

	def __init__(self, session, **kwargs):
		# You can pass name and other parameters if you want to
		super(UserView, self).__init__(User, session, **kwargs)

	def is_accessible(self):
		return current_user.is_authenticated() and current_user.is_admin()

class EndpointView(ModelView):

	def __init__(self, session, **kwargs):
		# You can pass name and other parameters if you want to
		super(EndpointView, self).__init__(Endpoint, session, **kwargs)

	def is_accessible(self):
		return current_user.is_authenticated() and current_user.is_admin()

class LogoutView(BaseView):
	@expose('/')
	def index(self):
		logout_user()
		form = LoginForm(request.form)
		return redirect(request.args.get("next") or url_for("index"))

if __name__ == "__main__":

	admin = Admin(app, name='OpenDASH')
	admin.add_view(UserView(session))
	admin.add_view(EndpointView(session))
	admin.add_view(LogoutView(name='Log out'))

	app.run(debug=True)