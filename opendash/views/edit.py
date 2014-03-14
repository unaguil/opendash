# -*- coding: utf-8 -*-

from flask import jsonify, request, render_template
from flask.ext.login import login_required, current_user

import rdflib
import json

from collections import defaultdict

from opendash import app, session
from opendash.form.login import LoginForm

from opendash.model.opendash_model import Prefix

DATA_TYPE = 'data_type'
OBJECT_TYPE = 'object_type'

def loadIgnoredPrefixes():
	ignored = []
	with open('opendash/files/ignored.txt') as f:
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
				'uri': shorten(str(p[0])),
				'datatype': data_type,
				'type': ref_type
			}

		properties.append(property)

	return properties

def infer_datatype(value):
	if value.isdigit():
		return 'http://www.w3.org/2001/XMLSchema#integer'
	else:
		return 'http://www.w3.org/2001/XMLSchema#string'

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

def get_long_prefix(uri):
	if '#' in uri:
		index = uri.find('#')
	else:
		index = uri.rfind('/')
		
	return uri[:index + 1]

def get_short_prefix(uri):
	index = uri.find(':')

	return uri[:index]

def shorten(uri):
	long_prefix = get_long_prefix(uri)
		
	prefix = session.query(Prefix).filter_by(uri=long_prefix).first()
	if prefix is None:
		prefix = Prefix(get_long_prefix(uri))

		session.add(prefix)
		session.commit()

	return uri.replace(prefix.uri, prefix.prefix + ':')

def enlarge(uri):
	short_prefix = get_short_prefix(uri)

	prefix = session.query(Prefix).filter_by(prefix=short_prefix).first()

	return uri.replace(prefix.prefix +':', prefix.uri)

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

		clazz['classURI'] = shorten(str(c[0]))

		clazz['properties'] = get_properties(g, graph, str(c[0]))
		classes.append(clazz)

	desc['classes'] = classes

	g.close()

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
		if c['classURI'] == clazz['classURI']:
			return c['properties']
	return []

def get_connections(clazz, desc):
	connections = {}

	for c in desc['classes']:
		entries = []
		for p1 in clazz['properties']:
			for p2 in c['properties']:
				if p1['uri'] == p2['uri']:
					entry = {}
					entry['name'] = p1['uri'] + ',' + p2['uri']
					entry['pair'] = (p2['uri'], p2['uri'])
					entries.append(entry)

		if len(entries) > 0:
			connections['classURI'] = c['classURI']
			connections['pairs'] = entries

	return connections

def process_line(endpoint, graph, mainclass, xvalues, xsubproperty, line):
	g = rdflib.ConjunctiveGraph('SPARQLStore')
	g.open(endpoint)

	if len(xsubproperty) > 0 and len(line['ysubproperty']) > 0:
		query = """SELECT ?x ?y FROM <%s> WHERE {
					?s a <%s> .
					?s <%s> ?p1 .
					?p1 <%s> ?x .
					?s <%s> ?p2 .
					?p2 <%s> ?y .
					} ORDER BY(?x)"""

		query = query % (graph, 
					enlarge(mainclass),
					enlarge(xsubproperty),
					enlarge(xvalues),
					enlarge(line['ysubproperty']),
					enlarge(line['yvalues'])
				)
	elif len(xsubproperty) > 0: 
		query = """SELECT ?x ?y FROM <%s> WHERE {
					?s a <%s> .
					?s <%s> ?p .
					?p <%s> ?x .
					?s <%s> ?y .
					} ORDER BY(?x)"""

		query = query % (graph, 
					enlarge(mainclass),
					enlarge(xsubproperty),
					enlarge(xvalues),
					enlarge(line['yvalues'])
				)
	elif len(line['ysubproperty']) > 0: 
		query = """SELECT ?x ?y FROM <%s> WHERE {
					?s a <%s> .
					?s <%s> ?x .
					?s <%s> ?p .
					?p <%s> ?y .
					} ORDER BY(?x)"""

		query = query % (graph, 
					enlarge(mainclass),
					enlarge(xvalues),
					enlarge(line['ysubproperty']),
					enlarge(line['yvalues'])
				)
	else: 
		query = """SELECT ?x ?y FROM <%s> WHERE {
					?s a <%s> .
					?s <%s> ?x .
					?s <%s> ?y .
					} ORDER BY(?x)"""

		query = query % (graph, 
					enlarge(mainclass),
					enlarge(xvalues),
					enlarge(line['yvalues'])
				)

	qres = g.query(query)

	data = []
	for row in qres:
		data.append({'x' : str(row[0]), 'y': str(row[1])})

	g.close()

	return data

def get_pairs(qres):
	data = []

	for row in qres:
		data.append((str(row[0]), str(row[1])))

	return data

def join_data(left_qres, right_qres):
	data = []

	right_dict = defaultdict(list)
	for row in right_qres:
		right_dict[str(row[0])].append(str(row[1]))

	for row in left_qres:
		x, z = str(row[0]), str(row[1])
		for y in right_dict[z]:
			data.append({'x' : x, 'y': y})

	return data

def process_connected_line(endpoint, graph, mainclass, xvalues, xsubproperty, line):
	left_g = rdflib.ConjunctiveGraph('SPARQLStore')
	left_g.open(endpoint)

	template = """SELECT ?x ?y FROM <%s> WHERE {
				?s a <%s> .
				?s <%s> ?x .
				?s <%s> ?y .
				} ORDER BY(?x)"""

	query = template % (graph, 
				enlarge(mainclass),
				enlarge(xvalues), 
				enlarge(line['pair'][0])
			)

	left_qres = left_g.query(query)

	right_g = rdflib.ConjunctiveGraph('SPARQLStore')
	right_g.open(line['endpoint'])

	query = template % (line['graph'], 
					enlarge(line['secondclass']),
					enlarge(line['pair'][1]),
					enlarge(line['yvalues'])
				)

	right_qres = right_g.query(query)

	data = join_data(left_qres, right_qres)

	left_g.close()
	right_g.close()

	return data

@app.route("/endpoints/get_data", methods=['POST'])
def get_data():
	endpoint = request.form['endpoint']
	graph = request.form['graph']
	mainclass = request.form['mainclass']
	xvalues = request.form['xvalues']
	xsubproperty = request.form['xsubproperty']
	line = json.loads(request.form['line'])

	if line['type'] == 'line':
		data = process_line(endpoint, graph, mainclass, xvalues, xsubproperty, line)
	elif line['type'] == 'connectedline':
		data = process_connected_line(endpoint, graph, mainclass, xvalues, xsubproperty, line)

	return jsonify(data=data)

def get_class_desc(classURI, desc):
	for c in desc['classes']:
		if c['classURI'] == classURI:
			return c
	return None

@app.route("/endpoints/get_datasource_connections", methods=['POST'])
def get_datasource_connections():
	first_endpoint = request.form['first_endpoint']
	first_graph = request.form['first_graph']
	mainclass = request.form['mainclass']

	second_endpoint = request.form['second_endpoint']
	second_graph = request.form['second_graph']

	first_desc = get_description(first_endpoint, first_graph) 
	second_desc = get_description(second_endpoint, second_graph)

	data = {}

	data['desc'] = second_desc;
	data['connections'] = []

	clazz = get_class_desc(mainclass, first_desc)

	connections = get_connections(clazz, second_desc)
	if len(connections) > 0:
		data['connections'].append(connections)

	return jsonify(data=data)