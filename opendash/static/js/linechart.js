google.load("visualization", "1", { packages:["corechart"] });

function updateChartLine(componentID, chart, lineID) {
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
			chart.data[lineID] = data.data;

			drawChart(componentID, chart);
	});
};

function drawChart(elementID, chart) {
	var arrayData = []

	titles = getTitles(chart);
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

	var lineChart = new google.visualization.LineChart(document.getElementById(elementID));
	lineChart.draw(data, options);
};

function getTitles(chart) {
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