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
  var limitSlider        = document.getElementById("limit-slider");
  var filterDiv          = document.getElementById("filter-div");
  var addFilterButton    = document.getElementById("add-filter");
  var removeFilterButton = document.getElementById("remove-filter");
  var valueDiv           = document.getElementById("value-div");
  var valueInput         = document.getElementById("value-input");
  var valueSetButton     = document.getElementById("set-value");
  var valueChoice        = document.getElementById("value-choice");
  source = currentDataSource();
  if (hasUserAddedSource(source)) {
    setFiltersForSelectedDataSource();
    addButton.style.visibility = "hidden";
    removeButton.style.visibility = "visible";
    if (source["filters_meta"].length > 0) {
      filterDiv.style.visibility = "visible";
      addFilterButton.style.visibility = "visible";
    } else {
      filterDiv.style.visibility = "hidden";
      addFilterButton.style.visibility = "hidden";
    }
    limitText.style.visibility = "visible";
    limitInput.style.visibility = "visible";
    limitButton.style.visibility = "visible";
    limitSlider.style.visibility = "visible";
    limitInput.value = userSourceForSource(source)["limit"];
  } else {
    addButton.style.visibility = "visible";
    removeButton.style.visibility = "hidden";
    filterDiv.style.visibility = "hidden";
    limitText.style.visibility = "hidden";
    limitInput.style.visibility = "hidden";
    limitButton.style.visibility = "hidden";
    limitSlider.style.visibility = "hidden";
    //Don't know why these are necessary...
    addFilterButton.style.visibility = "hidden";
    removeFilterButton.style.visibility = "hidden";
    valueDiv.style.visibility  = "hidden";
    valueInput.style.visibility = "hidden";
    valueSetButton.style.visibility = "hidden";
    valueChoice.style.visibility = "hidden";
  }
}

//Set the limit for the current data source
function setLimit() {
  var textBox = document.getElementById("limit-input");
  var slider  = document.getElementById("limit-slider");
  var limit = parseInt(textBox.value);
  //TO-DO: Some validation
  slider.value = limit;
  userSourceForSource(currentDataSource())["limit"] = limit;
  updateOutputText();
}

function limitSliderChanged() {
  var slider  = document.getElementById("limit-slider");
  var textBox = document.getElementById("limit-input");
  var limit = parseInt(slider.value);
  textBox.value = String(limit)
  userSourceForSource(currentDataSource())["limit"] = limit;
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
  var valueSetButton     = document.getElementById("set-value");
  var valueChoice        = document.getElementById("value-choice");
  var addFilterButton    = document.getElementById("add-filter");
  var removeFilterButton = document.getElementById("remove-filter");
  if (hasUserAddedFilter(filter)) {
    addFilterButton.style.visibility = "hidden";
    removeFilterButton.style.visibility = "visible";
    valueDiv.style.visibility = "visible";
    if (filter["type"] == "string") {
      valueInput.style.visibility     = "visible";
      valueSetButton.style.visibility = "visible";
      valueChoice.style.visibility    = "hidden";
      valueInput.value = userFilterForFilter(filter)["value"];
    } else {
      //Filter type is choice. FIXME: Assumes these are the only two types.
      valueInput.style.visibility     = "hidden";
      valueSetButton.style.visibility = "hidden";
      valueChoice.style.visibility    = "visible";
      addValueChoices();
    }
  } else {
    addFilterButton.style.visibility = "visible";
    removeFilterButton.style.visibility = "hidden";
    valueDiv.style.visibility = "hidden";
    //Don't know why need to do these:
    valueInput.style.visibility = "hidden";
    valueSetButton.style.visibility = "hidden";
    valueChoice.style.visibility    = "hidden";
  }
}

//Create a value choice and add it to the dropdown
function createValueChoice(choice,index) {
  var choicesSelect = document.getElementById("value-choice");
  var choiceElement = document.createElement("option");
  choiceElement.textContent = choice;
  choiceElement.id = "Value-Choice-" + index;
  choiceElement.value = index;
  choicesSelect.appendChild(choiceElement);
}

//Add value choices to the dropdown
function addValueChoices() {
  var choicesSelect = document.getElementById("value-choice");

  //Remove all current values from dropdown
  while (choicesSelect.firstChild) {
    choicesSelect.removeChild(choicesSelect.firstChild);
  }

  //Add new values
  var choices = currentFilter()["choose_from"];
  for (var i=0; i<choices.length; i++) {
    var choice = choices[i];
    createValueChoice(choice,i);
  }

  //If the user has already chosen a value, switch to that one
  var filter = currentFilter();
  if (hasUserAddedFilter(filter)) {
    var userFilter = userFilterForFilter(filter);
    var value = userFilter["value"];
    var index = filter["choose_from"].indexOf(value);
    var selectedOption = document.getElementById("Value-Choice-"+String(index));
    selectedOption.selected = "selected";
  }

  changedValueChoice();
}

//Called when the user has changed the value dropdown
function changedValueChoice() {
  var choicesSelect = document.getElementById("value-choice");
  var index = choicesSelect.value;
  var value = currentFilter()["choose_from"][index];

  var filter = currentFilter();
  var userSource = userSourceForSource(currentDataSource());
  if (!hasUserAddedFilter(filter)) {
    userSource["filters"].push({ "name": filter["name"],"value": value })

    var optionElement = document.getElementById("Filter-Option-" + filter["id"]);
    optionElement.textContent = filter["name"]+" (ADDED)";

    var removeFilterButton = document.getElementById("remove-filter");
    removeFilterButton.style.visibility = "visible";
  } else {
    var userFilter = userFilterForFilter(filter);
    userFilter["value"] = value;
  }

  updateOutputText();
}

//Show the value div (do not add the filter until a value is provided)
function addFilter() {
  var valueDiv        = document.getElementById("value-div");
  var valueInput      = document.getElementById("value-input");
  var valueSetButton  = document.getElementById("set-value");
  var valueChoice     = document.getElementById("value-choice");
  var addFilterButton = document.getElementById("add-filter");
  addFilterButton.style.visibility = "hidden";
  valueDiv.style.visibility = "visible";
  valueInput.value = "";
  if (currentFilter()["type"] == "string") {
    valueInput.style.visibility     = "visible";
    valueSetButton.style.visibility = "visible";
    valueChoice.style.visibility    = "hidden";
  } else {
    valueInput.style.visibility     = "hidden";
    valueSetButton.style.visibility = "hidden";
    valueChoice.style.visibility    = "visible";
    addValueChoices();
  }
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
  var textBox = document.getElementById("radius-input");
  var slider  = document.getElementById("radius-slider");
  var radius = parseFloat(textBox.value);
  slider.value = radius;
  //TO-DO: Some kind of validation
  search["radius"] = radius;
  updateOutputText();
}

function radiusSliderChanged() {
  var slider  = document.getElementById("radius-slider");
  var textBox = document.getElementById("radius-input");
  var radius  = parseFloat(slider.value);
  textBox.value = String(radius);
  search["radius"] = radius;
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
  if (validateSearch()) {
    httpPostAsync("/create_search",search,function(response) {
      console.log("Response: "+response);
      response = JSON.parse(response);
      if (response["id"] != null) {
        window.location.href = "/?s=" + response["id"];
      } /* else {
        alert("There was an error creating your search. Sorry!");
      } */ //This was getting called multiple times
    });
  }
}

//Return true if search is valid, otherwise return false and alert user
function validateSearch() {
  var sources = search["sources"];
  if (sources.length == 0) {
    alert("You must add at least one data source!");
    return false;
  }

  for (var i=0; i<sources.length; i++) {
    var source = sources[i];
    var limit = source["limit"];
    if (limit == null) {
      alert("The limit for a source must not be null!");
      return false;
    }
    if (limit < 0) {
      alert("The limit for a source must not be negative!");
      return false;
    }
  }

  var latitude  = search["latitude"];
  var longitude = search["longitude"];
  if (latitude == null || longitude == null) {
    alert("Latitude and Longitude must not be null!");
    return false;
  }
  var floatLat  = parseFloat(latitude);
  var floatLong = parseFloat(longitude);
  if (isNaN(floatLat) || isNaN(floatLong)) {
    alert("Latitude and Longitude must be numbers!");
    return false;
  }

  var radius = search["radius"];
  if (radius == null) {
    alert("Radius must not be null!");
    return false;
  }

  var floatRadius = parseFloat(radius);
  if (isNaN(floatRadius)) {
    alert("Radius must be a number!");
    return false;
  }

  if (floatRadius <= 0) {
    alert("Radius must be positive!");
    return false;
  }

  var name = search["name"];
  if (name == null) {
    alert("Search name must not be null!");
    return false;
  }

  return true;
}

//Thanks to: http://stackoverflow.com/questions/247483/http-get-request-in-javascript
function httpPostAsync(theUrl, object, callback)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            callback(xmlHttp.responseText);
        } else if (xmlHttp.status == 422) {
            callback(JSON.stringify({"Error_Status":xmlHttp.status}));
        }
    }
    xmlHttp.open("POST", theUrl, true); // true for asynchronous
    xmlHttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    // console.log("Request: "+JSON.stringify(object));
    xmlHttp.send(JSON.stringify(object));
}
