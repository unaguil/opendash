

//////////////////////////////// utility functions ///////////////////////////////////////

function findClass(uri) {
	for (var i = 0; i < desc.classes.length; i++) {
		if (desc.classes[i].classURI == uri)
			return i;
	}
	return -1;
};

function findProperty(uri, classID) {
	for (var i = 0; i < desc.classes[classID].properties.length; i++) {
		if (desc.classes[classID].properties[i].uri == uri)
			return i;
	}
	return -1;
};

function getObjectID(event) {
	var source = event.target || event.srcElement;
	var res = source.id.split("-");
	return res[res.length - 1];
};

function updateSelectComponent(componentID, values, property, onChange, addFilter) {
	addFilter = typeof addFilter == 'undefined' ? function f() { return true } : addFilter;

	$("#" + componentID).empty();

	for (var index = 0; index < values.length; index++) {
		if (addFilter(values[index]) == true)
			$("#" + componentID).append(new Option(values[index][property], index));
	}

	$("#" + componentID).change(function() {
		var index = $(this).val();
		onChange(componentID, values[index], index);					
	});	

	onChange(componentID, values[0], 0);
};

//////////////////////////////////////////////////////////////////////////////////////////

var id = 0;

function updateYSubProperty(componentID) {
	var tokens = componentID.split("-");
	var lineID = tokens[tokens.length - 1];

	chart.lines[lineID].yvalues = $('#' + componentID + ' :selected').text();
	chart.lines[lineID].ysubproperty = $('#yvalues-list-' + lineID + ' :selected').text();
};

function updateYValues(componentID) {
	var tokens = componentID.split("-");
	var lineID = tokens[tokens.length - 1];

	var classURI = $('#main-class-list :selected').text();
	var propertyURI = $('#' + componentID + ' :selected').text();

	var classID = findClass(classURI);
	var propertyID = findProperty(propertyURI, classID);

	$("#y-subproperty-list-" + componentID).remove();
	if (desc.classes[classID].properties[propertyID].type == 'object_type') {
		var snippet = '<select id="y-subproperty-list-' + componentID + '" class="form-control"></select>';

		$("#y-selected-property-" + componentID).append(snippet);

		var subpropertyClassID = findClass(desc.classes[classID].properties[propertyID].datatype);

		updateSelectComponent('y-subproperty-list-' + componentID, desc.classes[subpropertyClassID].properties, 'uri', updateYSubProperty, yValuesFilter);
	} else {
		chart.lines[lineID].yvalues = $('#' + componentID + ' :selected').text();
		chart.lines[lineID].ysubproperty = '';
	}

	chart.lines[lineID].type = 'line';

	updateChartLine('chart-div', chart, lineID, data);
};

function yValuesObjectFilter(property) {
	return (property.type == 'object_type' || $.inArray(property.datatype, getYValidDataTypes()) != -1);
};

function xValuesObjectFilter(property) {
	return (property.type == 'object_type' || $.inArray(property.datatype, getXValidDataTypes()) != -1);
};

function xValuesFilter(property) {
	return $.inArray(property.datatype, getXValidDataTypes()) != -1;
};

function yValuesFilter(property) {
	return $.inArray(property.datatype, getYValidDataTypes()) != -1;
};

function addLine(desc, id) {
	chart.lines[id]	 = {}

	var snippet = 	'<div id="configuration-' + id + '">' + 
						'<form class="form-horizontal" role="form">' +
							'<div class="form-group">' +
								'<label class="col-sm-2 control-label">Y</label>' +
								'<div id="y-selected-property-yvalues-list-' + id + '" class="col-sm-8">' +
									'<select id="yvalues-list-' + id + '" class="form-control"></select>' +
								'</div>' + 
								'<div class="col-sm-2">' +
									'<button id="remove-conf-button-' + id + '"type="button" class="btn btn-danger">X</button>' +
								'</div>' +
							'</div>' +
						'</form>' +
					'</div>';

	$('#lines-configuration').append(snippet);

	var classID = $("#main-class-list :selected").val();

	updateSelectComponent("yvalues-list-" + id, desc.classes[classID].properties, 'uri', updateYValues, yValuesObjectFilter);

	$("#remove-conf-button-" + id).click(function(event) {
		$('#configuration-' + id).remove();

		var lineID = getObjectID(event);
		delete chart.lines[lineID];

		
	});
};

function updateChart() {
	if (Object.keys(chart.lines).length > 0)
			drawChart('chart-div', chart, data);
	else
		$("#chart-div").empty();
};

function updateSecondaryYValues(connections, id, clazz) {
	var classID = $("#secondary-class-list :selected").val();

	$("#secondary-yvalues-list-" + id).empty();

	for (var index = 0; index < clazz.properties.length; index++) {
		var property = clazz.properties[index];
		if (property.type == 'object_type' || $.inArray(property.datatype, getYValidDataTypes()) != -1)
			$("#secondary-yvalues-list-" + id).append(new Option(property.uri, classID + ":" + index));
	}
};

function updateConnectionLabel(connections, id, clazz) {
	var res = $("#secondary-yvalues-list-" + id).val().split(":");
	var property = clazz['properties'][res[1]];

	$("#connection-label").text(property.connection);
};

function getValidDataTypes() {
	return $.merge(getXValidDataTypes(), getYValidDataTypes());

};

function getXValidDataTypes() {
	return 	[	'http://www.w3.org/2001/XMLSchema#integer',
				'http://www.w3.org/2001/XMLSchema#decimal',
				'http://www.w3.org/2001/XMLSchema#float',
				'http://www.w3.org/2001/XMLSchema#string'
			];			
};

function getYValidDataTypes() {
	return 	[	'http://www.w3.org/2001/XMLSchema#integer',
				'http://www.w3.org/2001/XMLSchema#decimal',
				'http://www.w3.org/2001/XMLSchema#float',
			];			
};

function removeIncompatibleTypes(classes, getValidDataTypes) {
	compatibleClasses = []
	for (var clazzIndex = 0; clazzIndex < classes.length; clazzIndex++) {
		properties = []

		clazz = classes[clazzIndex];
		for (var propertyIndex = 0; propertyIndex < clazz.properties.length; propertyIndex++) {
			property = clazz.properties[propertyIndex];
			if (property.type == 'object_type' || $.inArray(property.datatype, getValidDataTypes()) != -1)
				properties.push(property);
		}
		if (properties.length > 0)
			compatibleClasses.push({classURI : clazz.classURI, properties: properties})
	}

	return compatibleClasses;
};

function updateMainClass(componentID, selectedObj, descID) {
	chart.mainclass = desc.classes[descID].classURI;

	updateSelectComponent("main-xvalues-list", selectedObj.properties, 'uri', updateXValues, xValuesObjectFilter);
};

function updateXSubProperty() {
	chart.xvalues = $('#subproperty-list :selected').text();
	chart.xsubproperty = $('#main-xvalues-list :selected').text();
};

function updateXValues() {
	var classURI = $('#main-class-list :selected').text();
	var propertyURI = $('#main-xvalues-list :selected').text();

	var classID = findClass(classURI);
	var propertyID = findProperty(propertyURI, classID);

	$("#subproperty-list").remove();
	if (desc.classes[classID].properties[propertyID].type == 'object_type') {
		var snippet = '<select id="subproperty-list" class="form-control"></select>';

		$("#selected-property").append(snippet);

		var subpropertyClassID = findClass(desc.classes[classID].properties[propertyID].datatype);

		updateSelectComponent('subproperty-list', desc.classes[subpropertyClassID].properties, 'uri', updateXSubProperty, xValuesFilter);
	} else {
		chart.xvalues = $('#main-xvalues-list :selected').text();
		chart.xsubproperty = '';
	}
};

function processSource(endpointURL, graphName, dataSourceComponent) {
	$.post("/endpoints/get_description", { endpoint: endpointURL, graph: graphName }, function(data) {
		if (data.error) {
			dataSourceComponent.showAlert(data.error);
			return;
		}

		desc = data.desc;

		if (desc.classes.length > 0) {
			desc.classes = removeIncompatibleTypes(desc.classes, getValidDataTypes);			

			var snippet = 	'<div class="panel panel-default">' +
								'<div class="panel-heading">X axis</div>' +
								'<div class="panel-body">' +
									'<form class="form-horizontal" role="form">' +
										'<div class="form-group">' +
											'<label class="col-sm-2 control-label">Class</label>' + 
											'<div class="col-sm-10">' +
												'<select id="main-class-list" class="form-control"></select>' + 
											'</div>' + 
										'</div>' +
										'<div class="form-group">' +
											'<label class="col-sm-2 control-label">X</label>' + 
											'<div id="selected-property" class="col-sm-10">' +
												'<select id="main-xvalues-list" class="form-control"></select>' +
											'</div>' +
										'</div>' +
									'</form>' +
								'</div>' +
							'</div>' +
							'<div class="panel panel-default">' +
								'<div class="panel-heading">' +
									'Y value <button id="add-line-button" type="button" class="btn btn-primary btn-xs"><span class="glyphicon glyphicon-plus"></span></button>' +
								'</div>' +
								'<div id="lines-configuration" class="panel-body"></div>' +
							'</div>' +
							'<button id="connect-source-button" type="button" class="btn btn-primary">Add external data source <span class="glyphicon glyphicon-circle-arrow-right"></span></button>';

			$('#' + dataSourceComponent.getChild()).append(snippet);

			dataSourceComponent.disable();

			$("#main-configuration").append();

			chart.endpoint = desc.endpoint;
			chart.graph = desc.graph;

			updateSelectComponent("main-class-list", desc.classes, 'classURI', updateMainClass);

			$("#add-line-button").click(function(event) {
				$("#main-class-list").prop("disabled", true);
				$("#main-xvalues-list").prop("disabled", true);

				addLine(desc, id);
				id++;
			});

			$("#connect-source-button").click(function(event) {
				$("#main-class-list").prop("disabled", true);
				$("#main-xvalues-list").prop("disabled", true);

				chart.lines[id] = {};
				new ConnectedLine(id, desc, "#main-configuration");
				id++;
			});
		} else
			dataSourceComponent.showAlert("Dataset description was empty. No classes found.");
	});
};

function saveChart(report_id, chart_id) {
	chart_id = chart_id == -1 ? 'new' : chart_id;
	$.post("/report/" + report_id + "/chart/" + chart_id + "/save", 
		{ 	chart: JSON.stringify(chart),
			name: $("#chart-name-input").val()
		}, 
		function(data) {
			window.location.href = "/report/" + report_id + "/edit";
		}
	);
};

function updateChartName() {
	chart.name = $("#chart-name-input").val()

	updateChart();
}

function updateChartType() {
	chart.type = $("#select-chart-type").val()

	updateChart();
}

function deleteChart(report_id, chart_id) {
	$.post("/report/" + report_id + "/chart/" + chart_id + "/delete", function(data) {
		window.location.href = "/report/" + report_id + "/edit";
	});
};

/////////////////////////////////// initialization /////////////////////////////////////

var mainDataSource;

function init() {
	mainDataSource = new DataSourceComponent("Main data source", "main", "#main-configuration", processSource);
};

//////////////////////////////////////////////////////////////////////////////////////////