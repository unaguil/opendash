
from flask import jsonify, request
from flask.ext.login import login_required

from opendash import app, session
from opendash.model.opendash_model import Endpoint

import rdflib

from urllib2 import URLError

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

	try:
		qres = g.query("select distinct ?g where { graph ?g {?s ?p ?o} }")

		graphs = []
		for index, graph in enumerate(qres):
			graphs.append({'id': index, 'name': graph[0]})

		g.close()
		return jsonify(graphs=graphs)
	except URLError:
		return jsonify(error='Error getting endpoint graphs')