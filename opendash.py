# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask import jsonify, request

import random

app = Flask(__name__)

@app.route("/report")
def show_chart():
    return render_template('report.html')

@app.route("/endpoints")
def get_endpoints():
	endpoints = [
				{	'id': 0,
				 	'url': 'http://test1'
				}, 
				{	'id': 1,
					'url': 'http://test2'
				}, 
				{	'id': 2,
					'url': 'http://test3'
				}
				]

	return jsonify(endpoints=endpoints)

@app.route("/endpoints/<id>/graphs")
def get_endpoint_graphs(id):
	if id == '0':
		graphs = 	[
					{	'id': 0,
					  	'name': 'http://test1/graph1'
					}, 
					{ 	'id': 1,
						'name': 'http://test1/graph2'
					}
					]

		return jsonify(graphs=graphs)
	else:
		return jsonify(graphs=[])

@app.route("/endpoints/<endpointID>/graphs/<graphID>")
def get_source_description(endpointID, graphID):
	if endpointID == '0' and graphID == '0':
		desc = 	{ 	'endpointID': endpointID,
					'graphID': graphID,
					'classes': [
					{ 	'classURI': 'http://test1/class1',
						'properties': 	[
										{ 	'uri': 'http://test1/property1',
											'datatype': 'http://test1/type1'
										},
										{ 	'uri': 'http://test1/property2',
											'datatype': 'http://test1/type2'
										}		
										]
					},
					{ 	'classURI': 'http://test1/class2',
						'properties': 	[
										{ 	'uri': 'http://test1/property3',
											'datatype': 'http://test1/type1'
										},
										{ 	'uri': 'http://test1/property4',
											'datatype': 'http://test1/type2'
										}		
										]
					}]
				}

		return jsonify(desc=desc)
	else:
		return jsonify(desc=[])

@app.route("/endpoints/<endpointID>/graphs/<graphID>/data")
def get_data(endpointID, graphID):
	if endpointID == '0' and graphID == '0':
		data = 	[	random.randrange(1000), 
					random.randrange(1000),
					random.randrange(1000),
					random.randrange(1000)
				]

		return jsonify(data=data)
	else:
		return jsonify(data=data)

if __name__ == "__main__":
    app.run(debug=True)