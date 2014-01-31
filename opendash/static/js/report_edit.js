
function drawCharts(charts) {
	for (var id in charts) {
		for (var lineID in charts[id].lines) {
			updateChartLine('chart-' + id, charts[id], lineID);
		}
	}
};

function deleteChart(report_id, chart_id) {
	$.post("/report/" + report_id + "/chart/" + chart_id + "/delete", function(data) {
		$("#chart-container-" + chart_id).remove();
		$("#chart-counter-label").text($("#chart-counter-label").text() -1);
	});
};

function updateReport(report_id) {
	$.post("/report/" + report_id + "/update", { name : $("#report-name-input").val() });
};