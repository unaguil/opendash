
var selectedSchema = "";
var schemas = [];

function populateSchemaList() {
	var schemaList = document.getElementById("schema-list");
	for (var index = 0; index < schemas.length; index++) {
		var li = document.createElement('li');

		var link = document.createElement('a');

		var schemaName = schemas[index].name;
		link.id = schemaName;
		link.href = '#';
		link.onclick = schemaClick;
		link.innerHTML = schemaName;

		li.appendChild(link);
		schemaList.appendChild(li);
	}
};

function findSchema(schemaName) {
	for (var i = 0; i < schemas.length; i++)
		if (schemas[i].name == schemaName)
			return schemas[i];
}

function init() {
	var timestamp = new Date().getTime();
	$("#header").load("header.html?t=" + timestamp, function() {
		$("#version-selector").load("version-selector.html?t=" + timestamp, function() {
			getSchemas();
		}); 
	}); 
	$("#footer-bar").load("footer.html?=t" + timestamp); 
}

function getSchemas() {
	var xmlhttp;

	if (window.XMLHttpRequest) 	{
		// code for IE7+, Firefox, Chrome, Opera, Safari
		xmlhttp = new XMLHttpRequest();
	} else 	{
		// code for IE6, IE5
		xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
	} 

	xmlhttp.onreadystatechange = function() {
		if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
			var jsonResponse = eval("(" + xmlhttp.responseText + ")");

			schemas = jsonResponse.schemas;

			populateSchemaList();

			var urlVars = getUrlVars();
			if ('schemaName' in urlVars)
				selectSchema(findSchema(urlVars['schemaName']));
			else
				selectSchema(schemas[0]);

			if ('version' in urlVars)
				selectVersion(findVersion(urlVars['version']));
			else
				selectVersion(versions[0]);
		}
	};

	xmlhttp.open("GET","listschemas", true);
	xmlhttp.send();
};

function getUrlVars() {
	var vars = {};
	var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {
		vars[key] = value;
	});
	return vars;
};

function schemaClick(e) {
	selectSchema(findSchema(e.target.id));
}

function versionClick(e) {
	selectVersion(findVersion(e.target.id));
}

var selectedVersion = -1;
var versions = [];

function populateVersionList(schema) {
	var xmlhttp;

	if (window.XMLHttpRequest) 	{
		// code for IE7+, Firefox, Chrome, Opera, Safari
		xmlhttp = new XMLHttpRequest();
	} else 	{
		// code for IE6, IE5
		xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
	} 

	xmlhttp.onreadystatechange = function() {
		if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
			var jsonResponse = eval("(" + xmlhttp.responseText + ")");

			versions = jsonResponse.versions;

			document.getElementById("version-list").innerHTML = '';
			var versionList = document.getElementById("version-list");
			for (var index = 0; index < versions.length; index++) {
				var li = document.createElement('li');

				var link = document.createElement('a');

				var versionName = "Version " + versions[index].id;
				link.id = versions[index].id;
				link.onclick = versionClick;
				link.innerHTML = versionName;

				li.appendChild(link);
				versionList.appendChild(li);
			}

			selectVersion(versions[0]);
		}
	};

	xmlhttp.open("GET","listversions?schemaName=" + schema.name, true);
	xmlhttp.send();	
};

function selectSchema(schema) {
	selectedSchema = schema;
	populateVersionList(schema);
	document.getElementById("selected-dataset").innerHTML = schema.name;

	schemaChanged();
};

function selectVersion(version) {	
	selectedVersion = version;

	var showVersion = document.getElementById("selected-version");
	showVersion.innerHTML = "Version " + version.id;


	var viewButton = document.getElementById("view-version");
	if (viewButton != null)
		viewButton.href = "mapping.html?schemaName=" + selectedSchema.name + "&version=" + selectedVersion.id;

	versionChanged();
}

function findVersion(versionId) {
	for (var i = 0; i < versions.length; i++)
		if (versions[i].id == versionId)
			return versions[i];
}