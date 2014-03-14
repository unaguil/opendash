google.load("visualization", "1", { packages:["corechart"] });

function showAlert(componentID, msg) {
	$('#' + componentID).empty();
	
	alert = '<div class="alert alert-danger">'+ msg + '</div>';
	$('#' + componentID).append(alert);
};

function updateChartLine(componentID, chart, lineID, chart_data) {
	var post_data = { 	
		endpoint: chart.endpoint,
		graph: chart.graph,
		mainclass : chart.mainclass,
		xvalues : chart.xvalues,
		xsubproperty : chart.xsubproperty,
		line : JSON.stringify(chart.lines[lineID]) 
	};

	$.post("/endpoints/get_data", post_data, 
		function(data) {
			if (data.error)
				showAlert(componentID, data.error);
			else {
				chart_data[lineID] = data.data;

				drawChart(componentID, chart, chart_data);
			}
	});
};

function drawChart(elementID, chart, chart_data) {
	var arrayData = []

	titles = getTitles(chart);
	arrayData.push(titles);

	var someKey = Object.keys(chart_data)[0];
	var someData = chart_data[someKey];
	for (var rowIndex = 0; rowIndex < someData.length; rowIndex++) {
		var row = [];
		var xvalue = someData[rowIndex]['x'];
		row.push(xvalue);

		for (var key in chart_data) {
			var yvalue = parseInt(chart_data[key][rowIndex]['y']);
			row.push(yvalue);
		}

		arrayData.push(row);
	}

	var data = google.visualization.arrayToDataTable(arrayData);

	var options = {
		title: chart.name
	};

	var lineChart = new google.visualization.LineChart(document.getElementById(elementID));
	lineChart.draw(data, options);
};

function getTitles(chart) {
	var titles = []
	titles.push("x");

	var index = 0;
	for (var key in chart.lines) {
		titles.push(chart.lines[key].yvalues);
		index++;
	}

	return titles;
};