
function updateChartLine(chart, lineID) {
	$.post("/endpoints/get_data", 
		{ 	
			mainclass : chart.mainclass,
			xvalues : chart.xvalues,
			xsubproperty : chart.xsubproperty,
			line : JSON.stringify(chart.lines[lineID]) 
		}, 
		function(data) {
			chart.data[lineID] = data.data;

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