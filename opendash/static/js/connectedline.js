function ConnectedLine(id, desc, parent) {
	this.id = id;
	this.desc = desc;
	this.parent = parent;

	this.updateSecondaryDatasourceYValueList = function(componentID, selectedObj, descID) {
		chart.lines[this.id].endpoint = desc.endpoint;
		chart.lines[this.id].graph = desc.graph;
		chart.lines[this.id].type = 'connectedline';
		chart.lines[this.id].secondclass = $('#secondary-datasource-class-list-' + this.id + ' :selected').text();

		var connection = {};
		for (var index = 0; index < this.connections.connections.length; index++) {
			if (this.connections.connections[index].classURI == chart.lines[this.id].secondclass) {
				connection = this.connections.connections[index];
				break;
			}
		}

		var connectionName = $('#secondary-datasource-property-list-' + this.id + ' :selected').text();

		for (var index = 0; index < connection.pairs.length; index++) {
			if (connection.pairs[index].name == connectionName) {
				chart.lines[this.id].pair = connection.pairs[index].pair;
				break;
			}
		}

		chart.lines[this.id].yvalues = $('#secondary-datasource-yvalues-list-' + this.id + ' :selected').text();

		updateChartLine('chart-div', chart, this.id);
	};

	this.updateSecondaryDatasourcePropertyList = function(componentID, selectedObj, descID) {
		var classURI = $('#secondary-datasource-class-list-' + this.id + ' :selected').text();

		var properties = []
		for (var index = 0; index < this.connections.desc.classes.length; index++) {
			if (this.connections.desc.classes[index].classURI == classURI) {
				properties = this.connections.desc.classes[index].properties;
				break;
			}
		}
		updateSelectComponent("secondary-datasource-yvalues-list-" + this.id, properties, 'uri', this.updateSecondaryDatasourceYValueList.bind(this));
	};

	this.updateSecondaryDataSourceClassList = function(componentID, selectedObj, descID) {
		updateSelectComponent("secondary-datasource-property-list-" + this.id, selectedObj.pairs, 'name', this.updateSecondaryDatasourcePropertyList.bind(this));
	};

	this.processConnections = function(data) {
		this.connections = data.data;
		var snippet = 	'<div class="panel panel-default">' +
							'<div class="panel-heading">Y axis</div>' +
							'<div class="panel-body">' +
								'<form class="form-horizontal" role="form">' +
									'<div class="form-group">' +
										'<label class="col-sm-2 control-label">Class</label>' + 
										'<div class="col-sm-10">' +
											'<select id="secondary-datasource-class-list-' + this.id + '" class="form-control"></select>' + 
										'</div>' + 
									'</div>' +
									'<div class="form-group">' +
										'<label class="col-sm-2 control-label">Property</label>' + 
										'<div class="col-sm-10">' +
											'<select id="secondary-datasource-property-list-' + this.id + '" class="form-control"></select>' +
										'</div>' +
									'</div>' +
									'<div class="form-group">' +
										'<label class="col-sm-2 control-label">Y</label>' + 
										'<div class="col-sm-10">' +
											'<select id="secondary-datasource-yvalues-list-' + this.id + '" class="form-control"></select>' +
										'</div>' +
									'</div>' +
								'</form>' +
							'</div>' +
						'</div>';

		$("#" + this.datasourceComponent.getChild()).append(snippet);

		updateSelectComponent("secondary-datasource-class-list-" + this.id, this.connections['connections'], 'classURI', this.updateSecondaryDataSourceClassList.bind(this));
	};
	
	this.processSecondarySource = function(endpointURL, graphName, parent) {
		var post_data = { 
			first_endpoint: mainDataSource.getEndpoint(),
			first_graph: mainDataSource.getGraph(),
			mainclass: chart.mainclass,
			second_endpoint: endpointURL, 
			second_graph: graphName 
		};

		$.post("/endpoints/get_datasource_connections", post_data, this.processConnections.bind(this));
	};

	this.datasourceComponent = new DataSourceComponent("Data source " + (this.id + 1),
		"secondary-datasource-" + this.id, 
		this.parent, this.processSecondarySource.bind(this), true,
		function(datasource) {
			$("#secondary-datasource-" + this.id).remove();
			delete chart.lines[id];
		}.bind(this));
};