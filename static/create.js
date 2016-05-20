//Thanks to: http://stackoverflow.com/questions/247483/http-get-request-in-javascript
function httpGetAsync(theUrl, callback)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            callback(xmlHttp.responseText);
          }
    }
    xmlHttp.open("GET", theUrl, true); // true for asynchronous
    xmlHttp.send(null);
}

//To-Do: Add updating list of added sources/filters/values
//To-Do: Add remove buttons for each data source and filter
//To-Do: Add location/radius information fields
//To-Do: Add send button

//The main search object
var search = {}
search["sources"] = [];

//Get data about sources
var sources = []
httpGetAsync("/sources",function(response) {
  response = JSON.parse(response);
  sources  = response["sources"];
  for (var i = 0; i<sources.length; i++) {
    source = sources[i];
    createSource(source);
  }
});

//Return the source for the given id
function dataSourceForId(id) {
  for (var i = 0; i<sources.length; i++) {
    source = sources[i];
    if (source["id"] == id) {
      return source;
    }
  }
  return null;
}

//Return the user source for the given source
function userSourceForSource(source) {
  userSources = search["sources"];
  for (var i = 0; i<userSources.length; i++) {
    var userSource = userSources[i];
    if (userSource["id"] == source["id"]) {
      return userSource;
    }
  }
  return null;
}

//Has the user added the given source
function hasUserAddedSource(source) {
  return (userSourceForSource(source) != null);
}

//Return the current data source
function currentDataSource() {
  var dataSourcesSelect = document.getElementById("data-sources");
  var selectedSourceId = dataSourcesSelect.options[dataSourcesSelect.selectedIndex].value;
  return dataSourceForId(selectedSourceId);
}

//Add a data source to the dropdown menu
//Thanks to: http://stackoverflow.com/questions/9895082/javascript-populate-drop-down-list-with-array
function createSource(source) {
  var dataSourcesSelect = document.getElementById("data-sources");
  var option = document.createElement("option");
  option.textContent = source["name"];
  option.id = "Source-Option-" + source["id"];
  option.value = source["id"];
  dataSourcesSelect.appendChild(option);
}

//Add a source to the search
function addDataSource() {
  source = currentDataSource();
  if (!hasUserAddedSource(source)) {
    search["sources"].push({ "id": source["id"], "filters": [], "limit": 10 });
    changedToDataSource();

    var optionElement = document.getElementById("Source-Option-" + source["id"]);
    optionElement.textContent = source["name"]+" (ADDED)";

    updateOutputText();
  }
}

//Remove a source from the search
function removeDataSource() {
  source = currentDataSource();
  if (hasUserAddedSource(source)) {
    var index = search["sources"].indexOf(userSourceForSource(source));
    if (index > -1) {
      search["sources"].splice(index,1);
      changedToDataSource();

      var optionElement = document.getElementById("Source-Option-" + source["id"]);
      optionElement.textContent = source["name"];

      updateOutputText();
    }
  }
 }

//Call when the dropdown changed
function changedToDataSource() {
  var addButton          = document.getElementById("add-source");
  var removeButton       = document.getElementById("remove-source");
  var limitText          = document.getElementById("limit-text");
  var limitInput         = document.getElementById("limit-input");
  var limitButton        = document.getElementById("set-limit");
  var filterDiv          = document.getElementById("filter-div");
  var addFilterButton    = document.getElementById("add-filter");
  var removeFilterButton = document.getElementById("remove-filter");
  var valueDiv           = document.getElementById("value-div");
  source = currentDataSource();
  if (hasUserAddedSource(source)) {
    setFiltersForSelectedDataSource();
    addButton.style.visibility = "hidden";
    removeButton.style.visibility = "visible";
    filterDiv.style.visibility = "visible";
    limitText.style.visibility = "visible";
    limitInput.style.visibility = "visible";
    limitButton.style.visibility = "visible";
    limitInput.value = userSourceForSource(source)["limit"];
  } else {
    addButton.style.visibility = "visible";
    removeButton.style.visibility = "hidden";
    filterDiv.style.visibility = "hidden";
    limitText.style.visibility = "hidden";
    limitInput.style.visibility = "hidden";
    limitButton.style.visibility = "hidden";
    //Don't know why these are necessary...
    addFilterButton.style.visibility = "hidden";
    removeFilterButton.style.visibility = "hidden";
    valueDiv.style.visibility  = "hidden";
  }
}

//Set the limit for the current data source
function setLimit() {
  var element = document.getElementById("limit-input");
  var limit = element.value;
  //TO-DO: Some validation
  userSourceForSource(currentDataSource())["limit"] = parseInt(limit);
  updateOutputText();
}

//Add a filter to the dropdown menu
function createFilter(filter) {
  var filtersSelect = document.getElementById("filters");
  var option = document.createElement("option");
  option.textContent = filter["name"];
  if (hasUserAddedFilter(filter)) {
    option.textContent = filter["name"]+" (ADDED)";
  }
  option.value = filter["id"];
  option.id = "Filter-Option-" + filter["id"];
  filtersSelect.appendChild(option);
}

//Set the filters for the selected data source
function setFiltersForSelectedDataSource() {
  source = currentDataSource();
  filters = source["filters_meta"];
  //Remove all current filters from dropdown
  var filterSelect = document.getElementById("filters");
  while (filterSelect.firstChild) {
    filterSelect.removeChild(filterSelect.firstChild);
  }
  //Add new filters
  for (var j = 0; j<filters.length; j++) {
    createFilter(filters[j]);
  }

  changedToFilter();
}

//Return the filter for a given id
//***Assumes the filter's data source is the current one
function filterForId(id) {
  source = currentDataSource();
  filters = source["filters_meta"];
  for (var i = 0; i<filters.length; i++) {
    var filter = filters[i];
    if (filter["id"] == id) {
      return filter;
    }
  }
  return null;
}

//Return the current filter
function currentFilter() {
  var filterSelect = document.getElementById("filters");
  return filterForId(filterSelect.value);
}

//Return the userFilter for the given filter
//***Assumes the filter is for the currentSource
function userFilterForFilter(filter) {
  var userSource = userSourceForSource(currentDataSource());
  var userFilters = userSource["filters"];
  for (var i = 0; i<userFilters.length; i++) {
    var userFilter = userFilters[i];
    if (userFilter["name"] == filter["name"]) {
      return userFilter;
    }
  }
  return null;
}

//Has the user added the given filter
function hasUserAddedFilter(filter) {
  return (userFilterForFilter(filter) != null);
}

//Call when the dropdown changed
function changedToFilter() {
  var filter = currentFilter();
  var valueDiv           = document.getElementById("value-div");
  var valueInput         = document.getElementById("value-input");
  var addFilterButton    = document.getElementById("add-filter");
  var removeFilterButton = document.getElementById("remove-filter");
  if (hasUserAddedFilter(filter)) {
    addFilterButton.style.visibility = "hidden";
    removeFilterButton.style.visibility = "visible";
    valueDiv.style.visibility = "visible";
    valueInput.value = userFilterForFilter(filter)["value"];
  } else {
    addFilterButton.style.visibility = "visible";
    removeFilterButton.style.visibility = "hidden";
    valueDiv.style.visibility = "hidden";
  }
}

//Show the value div (do not add the filter until a value is provided)
function addFilter() {
  var valueDiv        = document.getElementById("value-div");
  var valueInput      = document.getElementById("value-input");
  var addFilterButton = document.getElementById("add-filter");
  addFilterButton.style.visibility = "hidden";
  valueDiv.style.visibility = "visible";
  valueInput.value = "";
}

//Set the value for the current filter
function setValue() {
  var filter = currentFilter();
  var valueInput = document.getElementById("value-input");
  var userSource = userSourceForSource(currentDataSource());
  if (!hasUserAddedFilter(filter)) {
    userSource["filters"].push({ "name": filter["name"],"value": valueInput.value })
    changedToFilter()

    var optionElement = document.getElementById("Filter-Option-" + filter["id"]);
    optionElement.textContent = filter["name"]+" (ADDED)";
  } else {
    var userFilter = userFilterForFilter(filter);
    userFilter["value"] = valueInput.value;
  }

  updateOutputText();
}

//Remove the current filter
function removeFilter() {
  filter = currentFilter();
  if (hasUserAddedFilter(filter)) {
    var userSource = userSourceForSource(currentDataSource());
    var index = userSource["filters"].indexOf(userFilterForFilter(filter));
    if (index > -1) {
      userSource["filters"].splice(index,1);
      changedToFilter();

      var optionElement = document.getElementById("Filter-Option-" + filter["id"]);
      optionElement.innerHTML = filter["name"];

      updateOutputText();
    }
  }
}

//Update the output text
function updateOutputText() {
  var element = document.getElementById("search-object-output")
  element.innerHTML = JSON.stringify(search,null,2);
}

//LOCATION FUNCTIONS

function setLatitude() {
  var element = document.getElementById("lat-input");
  var latitude = element.value;
  //TO-DO: Some kind of validation
  search["latitude"] = latitude;
  updateOutputText();
}

function setLongitude() {
  var element = document.getElementById("lon-input");
  var longitude = element.value;
  //TO-DO: Some kind of validation
  search["longitude"] = longitude;
  updateOutputText();
}

function getLocation() {
  if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(updateLocation);
  }
}

function updateLocation(position) {
  search["latitude"]  = position.coords.latitude;
  search["longitude"] = position.coords.longitude;
  var latInput = document.getElementById("lat-input");
  var lonInput = document.getElementById("lon-input");
  latInput.value = position.coords.latitude;
  lonInput.value = position.coords.longitude;
  updateOutputText();
}

function setRadius() {
  var element = document.getElementById("radius-input");
  var radius = element.value;
  //TO-DO: Some kind of validation
  search["radius"] = parseFloat(radius);
  updateOutputText();
}

//METADATA FUNCTIONS

function setName() {
  var element = document.getElementById("name-input");
  var name = element.value;
  //TO-DO: Some kind of validation
  search["name"] = name;
  updateOutputText();
}

//SUBMIT FUNCTIONS

function submit() {
  //TO-DO: Validation of required fields
  httpPostAsync("/create_search",search,function(response) {
    console.log("Response: "+response);
    response = JSON.parse(response);
    if (response["id"] != null) {
      window.location.href = "/?s=" + response["id"];
    } else {
      console.log("null search id");
    }
  });
}

//Thanks to: http://stackoverflow.com/questions/247483/http-get-request-in-javascript
function httpPostAsync(theUrl, object, callback)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            callback(xmlHttp.responseText);
          }
    }
    xmlHttp.open("POST", theUrl, true); // true for asynchronous
    xmlHttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    console.log("Request: "+JSON.stringify(object));
    xmlHttp.send(JSON.stringify(object));
}
