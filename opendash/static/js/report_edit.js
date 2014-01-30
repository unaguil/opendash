
function drawCharts(charts) {
	for (var id in charts) {
		for (var lineID in charts[id].lines) {
			updateChartLine('chart-' + id, charts[id], lineID);
		}
	}
};