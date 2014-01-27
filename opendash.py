# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask import jsonify, request
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView

import rdflib
import json
import random

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from model.opendash_model import User, Endpoint

app = Flask(__name__)

DATA_TYPE = 'data_type'
OBJECT_TYPE = 'object_type'

@app.route("/")
def render_index():
	return render_template('index.html')

@app.route("/report")
def render_report():
	return render_template('report.html')

@app.route("/endpoints")
def get_endpoints():
	available_endpoints = session.query(Endpoint).all()

	endpoints = []
	for endpoint in available_endpoints:
		endpoints.append({'id': endpoint.id, 'url': endpoint.url })

	return jsonify(endpoints=endpoints)

@app.route("/endpoints/get_graphs", methods=['POST'])
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
		ref_type, data_type = get_property_type(g, graph, clazz, str(p[0]))
		property = {
				'uri': str(p[0]),
				'datatype': data_type,
				'type': ref_type
			}

		properties.append(property)

	return properties

def infer_datatype(value):
	if type(value) is str or type(value) is unicode:
		return 'http://www.w3.org/2001/XMLSchema#string'
	elif type(value) is int:
		return 'http://www.w3.org/2001/XMLSchema#integer'
	return ''

def get_object_type(g, graph, value):
	query = """SELECT ?type FROM <%s> WHERE {
				<%s> a ?type .
				}"""

	query = query % (graph, value)

	qres = g.query(query)

	for value in qres:
		return str(value[0])

def get_property_type(g, graph, clazz, property):
	query = """SELECT ?value FROM <%s> WHERE {
				?s a <%s> .
				?s <%s> ?value .
				} LIMIT 1"""

	query = query % (graph, clazz, property)

	qres = g.query(query)
	for value in qres:
		if type(value[0]) is rdflib.term.Literal:
			if value[0].datatype is not None and value[0].datatype != '':
				return DATA_TYPE, str(value[0].datatype)
			else:
				return DATA_TYPE, infer_datatype(str(value[0]))

		return OBJECT_TYPE, get_object_type(g, graph, str(value[0]))

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
def get_compatible_classes():
	endpoint = request.form['endpoint']
	graph = request.form['graph']
	clazz = request.form['class']

	desc = get_description(endpoint, graph)

	connections = get_connections(clazz, desc)

	return jsonify(connections=connections)

@app.route("/endpoints/get_data", methods=['POST'])
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

	print query

	qres = g.query(query)

	data = []
	for row in qres:
		data.append({'x' : str(row[0]), 'y': str(row[1])})

	return jsonify(data=data)

@app.route("/endpoints/get_class_data", methods=['POST'])
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

engine = create_engine('sqlite:///opendash.db')
Session = sessionmaker(bind=engine)
session = Session()

if __name__ == "__main__":

	admin = Admin(app, name='OPENDASH')
	admin.add_view(ModelView(User, session))
	admin.add_view(ModelView(Endpoint, session))

	app.run(debug=True)