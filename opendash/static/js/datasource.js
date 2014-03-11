

function DataSourceComponent(title, name, parent, processSource, removable, removed) {
	this.title = title;
	this.name = name;
	this.parent = parent;
	this.processSource = processSource;
	this.child = "child-" + this.name;
	this.removable = removable || false;
	this.removed = removed || null;

	this.getTitle = function() {
		if (this.removable)
			return this.title + ' <button id="remove-datasource-button-' + this.name + '"type="button" class="btn btn-danger">X</button>';
		else
			return this.title;
	}

	this.addDataSource = function() {
		var snippet =	'<div id="' +  this.name + '"class="panel panel-default">' +
						'<div class="panel-heading">' +
							this.getTitle() + 
						'</div>' +
						'<div class="panel-body">' +
							'<form class="form-horizontal" role="form">' +
								'<div class="form-group">' +
									'<label class="col-sm-2 control-label">Dataset</label>' +
									'<div class="col-sm-10">' +
										'<select id="dataset-list-' + this.name + '" class="form-control"></select>' +
									'</div>' +
								'</div>' +
								'<div class="form-group">' +
									'<label class="col-sm-2 control-label">Graph</label>' +
									'<div class="col-sm-10">' +
										'<select id ="graph-list-' + this.name + '" class="form-control"></select>' +
									'</div>' +
								'</div>' +
								'<div class="form-group">' +
									'<div class="col-sm-offset-2 col-sm-10">' +
										'<button id="select-source-button-' + this.name + '" type="button" class="btn btn-success">Apply</button>' +
									'</div>' +
								'</div>' +
							'</form>' +
							'<div id="' + this.child + '"></div>'
						'</div>' +
					'</div>';

		$(this.parent).append(snippet);

		if (removable) {
			var that = this;
			$("#remove-datasource-button-" + this.name).click(function(event) {
				that.removed(that);
			});
		}
	};

	this.populateEndpoints = function() {
		var that = this;
		$.getJSON("/endpoints", function(data) {
			updateSelectComponent("dataset-list-" + that.name, data.endpoints, 'url', that.updateGraphList)
		});

		$("#select-source-button-" + that.name).click(function(event) {
			$("#dataset-list-" + that.name).prop("disabled", true);
			$("#graph-list-" + that.name).prop("disabled", true);
			$("#select-source-button-" + that.name).prop("disabled", true);

			that.endpointURL = $("#dataset-list-" + that.name + " :selected").text();
			that.graphName = $("#graph-list-" + that.name + " :selected").text();

			that.processSource(that.endpointURL, that.graphName, "#" + that.child);
		});
	};

	this.getEndpoint = function() {
		return this.endpointURL;
	};

	this.getGraph = function() {
		return this.graphName;
	}

	this.updateGraphList = function (componentID, endpoint, index) {
		var that = this;
		$.post("/endpoints/get_graphs", { endpoint: endpoint.url }, function(data) {
			updateSelectComponent("graph-list-" + that.name, data.graphs, 'name', function() {});
		});
	};

	this.getChild = function() {
		return this.child;
	};

	this.addDataSource();
	this.populateEndpoints();
};