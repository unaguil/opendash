function DataSourceComponent(title, id, parent, process, removable, onRemove) {
	this.id = id;
	this.title = title;
	this.parent = parent;
	this.process = process;
	this.child = "child-" + this.id;
	this.removable = removable || false;
	this.onRemove = onRemove || null;

	this.getTitle = function() {
		if (this.removable)
			return this.title + ' <button id="remove-datasource-button-' + this.id + '"type="button" class="btn btn-danger">X</button>';
		else
			return this.title;
	}

	this.addDataSource = function() {
		var snippet =	'<div id="' +  this.id + '"class="panel panel-default">' +
						'<div class="panel-heading">' +
							this.getTitle() + 
						'</div>' +
						'<div class="panel-body">' +
							'<form class="form-horizontal" role="form">' +
								'<div class="form-group">' +
									'<label class="col-sm-2 control-label">Dataset</label>' +
									'<div class="col-sm-10">' +
										'<select id="dataset-list-' + this.id + '" class="form-control"></select>' +
									'</div>' +
								'</div>' +
								'<div class="form-group">' +
									'<label class="col-sm-2 control-label">Graph</label>' +
									'<div class="col-sm-10">' +
										'<select id ="graph-list-' + this.id + '" class="form-control"></select>' +
									'</div>' +
								'</div>' +
								'<div class="form-group">' +
									'<div class="col-sm-offset-2 col-sm-10">' +
										'<button id="select-source-button-' + this.id + '" type="button" class="btn btn-success">Apply</button>' +
									'</div>' +
								'</div>' +
							'</form>' +
							'<div id="' + this.child + '"></div>' +
						'</div>' +
					'</div>';

		$(this.parent).append(snippet);

		if (removable) {
			$("#remove-datasource-button-" + this.id).click(function(event) {
				this.onRemove(this);
			}.bind(this));
		}
	};

	this.populateEndpoints = function() {
		$.getJSON("/endpoints", function(data) {
			updateSelectComponent("dataset-list-" + this.id, data.endpoints, 'url', this.updateGraphList.bind(this))
		}.bind(this));

		$("#select-source-button-" + this.id).click(function(event) {
			$("#dataset-list-" + this.id).prop("disabled", true);
			$("#graph-list-" + this.id).prop("disabled", true);
			$("#select-source-button-" + this.id).prop("disabled", true);

			this.endpointURL = $("#dataset-list-" + this.id + " :selected").text();
			this.graphName = $("#graph-list-" + this.id + " :selected").text();

			this.process(this.endpointURL, this.graphName, "#" + this.child);
		}.bind(this));
	};

	this.getEndpoint = function() {
		return this.endpointURL;
	};

	this.getGraph = function() {
		return this.graphName;
	}

	this.updateGraphList = function (componentID, endpoint, index) {
		$('#' + this.child).empty();

		$.post("/endpoints/get_graphs", { endpoint: endpoint.url }, function(data) {
			if (data.error) {
				alert = '<div class="alert alert-danger">'+ data.error + '</div>';
				$('#' + this.child).append(alert);
				$('#' + "graph-list-" + this.id).empty();
			}
			else
				updateSelectComponent("graph-list-" + this.id, data.graphs, 'name', function() {});
		}.bind(this));
	};

	this.getChild = function() {
		return this.child;
	};

	this.addDataSource();
	this.populateEndpoints();
};