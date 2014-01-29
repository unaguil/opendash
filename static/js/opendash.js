

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

function updateSelectComponent(componentID, values, property, onChange) {
	$("#" + componentID).empty();

	for (var index = 0; index < values.length; index++)
		$("#" + componentID).append(new Option(values[index][property], index));

	$("#" + componentID).change(function() {
		var index = $(this).val();
		onChange(componentID, values[index], index);					
	});	

	onChange(componentID, values[0], 0);
};

//////////////////////////////////////////////////////////////////////////////////////////


var chart = {};
chart.data = {};
chart.lines = {};
chart.classes = {};
connections = null;

var id = 0;

function getTitles() {
	var titles = []
	titles.push("x");

	var index = 0;
	for (var key in chart.lines) {
		titles.push("Title " + index);
		index++;
	}

	var index = 0;
	for (var key in chart.classes) {
		titles.push("Title " + index);
		index++;
	}

	return titles;
};

function updateChartLine(desc, chart, lineID) {
	var post_data = { 	endpoint: desc.endpoint, 
						graph: desc.graph,
						mainclass: chart.mainclass,
						xvalues: chart.xvalues,
						subproperty: chart.subproperty,
						yvalues: chart.lines[lineID].yvalues
					};

	$.post("endpoints/get_data", 
		post_data, 
		function(data) {
			chart.data[lineID] = data.data;

			drawChart();
	});
};

function updateChartClass(desc, chart, classID) {
	$.post("endpoints/get_class_data", 
		{ 	endpoint: desc.endpoint, 
			graph: desc.graph,
			mainclass: chart.mainclass,
			xvalues: chart.xvalues,
			secondaryclass: chart.classes[classID].secondaryClass,
			yvalues: chart.classes[classID].yvalues,
			connection: chart.classes[classID].connection
		}, 
		function(data) {
			chart.data[classID] = data.data;

			drawChart();
	});
};

function drawChart() {
	var arrayData = []

	titles = getTitles();
	arrayData.push(titles);

	var someKey = Object.keys(chart.data)[0];
	var data = chart.data[someKey];
	for (var rowIndex = 0; rowIndex < data.length; rowIndex++) {
		var row = [];
		var xvalue = data[rowIndex]['x'];
		row.push(xvalue);

		for (var key in chart.data) {
			var yvalue = parseInt(chart.data[key][rowIndex]['y']);
			row.push(yvalue);
		}

		arrayData.push(row);
	}

	var data = google.visualization.arrayToDataTable(arrayData);

	var options = {
		title: 'Some title'
	};

	var lineChart = new google.visualization.LineChart(document.getElementById('chart-div'));
	lineChart.draw(data, options);
};

function addLine(desc, id) {
	var snippet = 	'<div id="configuration-' + id + '">' + 
						'<form class="form-horizontal" role="form">' +
							'<div class="form-group">' +
								'<label class="col-sm-2 control-label">Y</label>' +
								'<div class="col-sm-8">' +
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

	for (var index = 0; index < desc.classes[classID].properties.length; index++) {
		var property = desc.classes[classID].properties[index];

		if (property.type == 'object_type' || $.inArray(property.datatype, getYValidDataTypes()) != -1)	
			$("#yvalues-list-" + id).append(new Option(property.uri, classID + ":" + index));
	}

	$("#remove-conf-button-" + id).click(function(event) {
		$('#configuration-' + id).remove();

		var lineID = getObjectID(event);
		delete chart.lines[lineID];

		if (Object.keys(chart.lines).length > 0)
			drawChart();
		else
			$("#chart-div").empty();
	});

	$("#yvalues-list-" + id).change(function(event) {
		var lineID = getObjectID(event);
		var res = $(this).val().split(":");

		chart.lines[lineID].yvalues = desc.classes[res[0]].properties[res[1]].uri;
		updateChartLine(desc, chart, lineID);
	});

	var line = {};
	line.yvalues = desc.classes[classID].properties[0].uri;
	chart.lines[id] = line;
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

function addClass(desc, id) {
	var snippet = 	'<div id="class-configuration-' + id + '" class="well">' +
						'<span id="connection-label" class="label label-default">Connection:</span>' + 
						'<form class="form-horizontal" role="form">' +
							'<div class="form-group">' +
								'<label class="col-sm-2 control-label">Class</label>' + 
								'<div class="col-sm-10">' +
									'<select id="secondary-class-list-' + id + '" class="form-control"></select>' + 
								'</div>' + 
							'</div>' +
							'<div class="form-group">' +
								'<label class="col-sm-2 control-label">Y</label>' + 
								'<div class="col-sm-10">' +
									'<select id="secondary-yvalues-list-' + id + '" class="form-control"></select>' +
								'</div>' +
							'</div>' +
							'<button id="remove-class-conf-button-' + id + '"type="button" class="btn btn-danger">Remove</button>' +
						'</form>' +
					'</div>';

	$.post("endpoints/get_connections", 
		{ 	endpoint: desc.endpoint, 
			graph: desc.graph, 
			class: chart.mainclass,
		}, 
		function(data) {
			connections = removeIncompatibleTypes(data.connections, getYValidDataTypes);

			if (connections.length > 0) {
				$('#classes-configuration').append(snippet);

				$("#remove-class-conf-button-" + id).click(function(event) {
					$('#class-configuration-' + id).remove();
				});

				$("#secondary-class-list-" + id).change(function() {
					var clazz = connections[$(this).val()];
					updateSecondaryYValues(connections, id, clazz);				
				});

				$("#secondary-yvalues-list-" + id).change(function() {
					var clazz = connections[$(this).val()];
					updateConnectionLabel(connections, id, clazz);

					var classID = getObjectID(event);
					var res = $(this).val().split(":");

					property = connections[res[0]].properties[res[1]];
					chart.classes[classID].yvalues = property.uri;
					chart.classes[classID].connection = property.connection;
					
					updateChartClass(desc, chart, classID);
				});

				for (var index = 0; index < connections.length; index++) {
					var clazz = connections[index];
					$("#secondary-class-list-" + id).append(new Option(clazz.classURI, index));
				}

				var clazz = connections[0];
				updateSecondaryYValues(connections, id, clazz);
				updateConnectionLabel(connections, id, clazz);

				var classConf = {}
				classConf.secondaryClass = clazz['classURI'];
				classConf.yvalues = clazz.properties[0].uri;
				classConf.connection = clazz.properties[0].connection;

				chart.classes[id] = classConf;

				updateChartClass(desc, chart, id);
			}
		}
	);
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
	updateSelectComponent("main-xvalues-list", selectedObj.properties, 'uri', updateXValues);

	chart.mainclass = desc.classes[descID].classURI;
	chart.xvalues = desc.classes[descID].properties[0].uri;
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

		for (var index = 0; index < desc.classes[subpropertyClassID].properties.length; index++) {
			var property = desc.classes[subpropertyClassID].properties[index];

			if ($.inArray(property.datatype, getXValidDataTypes()) != -1)	
				$("#subproperty-list").append(new Option(property.uri, subpropertyClassID + ":" + index));
		}

		$("#subproperty-list").change(function() {
			var res = $(this).val().split(":");

			chart.xvalues = desc.classes[res[0]].properties[res[1]].uri;			
			chart.subproperty = $('#main-xvalues-list :selected').text();
		});

		chart.xvalues = desc.classes[classID].properties[propertyID].uri;
		chart.subproperty = $('#main-xvalues-list :selected').text();
	} else
		chart.xvalues = $('#main-xvalues-list :selected').text();
		chart.subproperty = '';
}

function processSource() {
	var endpointURL = $("#dataset-list :selected").text();
	var graphName = $("#graph-list :selected").text();

	$.post("endpoints/get_description", { endpoint: endpointURL, graph: graphName }, function(data) {
		desc = data.desc;

		desc.classes = removeIncompatibleTypes(desc.classes, getValidDataTypes);			

		var snippet = 	'<div class="well">' +
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
								'<button id="add-line-button" type="button" class="btn btn-primary">Add property</button>' +
								'<button id="add-class-button" type="button" class="btn btn-primary">Add class</button>' +
							'</form> </br>' +
							'<div class="panel panel-default">' +
								'<div class="panel-heading">' +
									'<h3 class="panel-title">Properties</h3>' +
									'</div>' +
								'<div id="lines-configuration" class="panel-body"></div>' +
							'</div>' +
							'<div class="panel panel-default">' +
								'<div class="panel-heading">' +
									'<h3 class="panel-title">Classes</h3>' +
									'</div>' +
								'<div id="classes-configuration" class="panel-body"></div>' +
							'</div>' +
						'</div>';

		$('#main-configuration').append(snippet);

		updateSelectComponent("main-class-list", desc.classes, 'classURI', updateMainClass);

		$("#add-line-button").click(function(event) {
			$("#main-class-list").prop("disabled", true);
			$("#main-xvalues-list").prop("disabled", true);

			addLine(desc, id);;
			updateChartLine(desc, chart, id);
			id++;
		});

		$("#add-class-button").click(function(event) {
			$("#main-class-list").prop("disabled", true);
			$("#main-xvalues-list").prop("disabled", true);

			addClass(desc, id);;
			id++;
		});
	});
};

///////////////////////////////// source management //////////////////////////////////////

function populateEndpoints() {
	$.getJSON("endpoints", function(data) {
		updateSelectComponent("dataset-list", data.endpoints, 'url', updateGraphList)
	});

	$("#select-source-button").click(function(event) {
		$("#dataset-list").prop("disabled", true);
		$("#graph-list").prop("disabled", true);
		$(this).prop("disabled", true);

		processSource();
	});
};

function updateGraphList(componentID, endpoint, index) {
	$.post("endpoints/get_graphs", { endpoint: endpoint.url }, function(data) {
		updateSelectComponent("graph-list", data.graphs, 'name', function() {});
	});
};

//////////////////////////////////////////////////////////////////////////////////////////

/////////////////////////////////// initialization /////////////////////////////////////

function init() {
	populateEndpoints();
};

//////////////////////////////////////////////////////////////////////////////////////////