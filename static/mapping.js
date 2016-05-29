function initMap() {
    var myLatLng = {lat: 41.8781, lng: -87.6298};
    // Create a map object and specify the DOM element for display.

    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12,
        center: myLatLng
                                  });
        //parse JSON file from search, iterate through and add points
        searchID = QueryString.s;
        if (searchID) {
          document.getElementById("searchName").innerHTML = "Loading...";
          httpGetAsync("http://127.0.0.1:5000/search-results/"+searchID, function(response) {
            var bounds = new google.maps.LatLngBounds();
            response = JSON.parse(response);
            document.getElementById("searchName").innerHTML = "<u>"+response["name"]+"</u>";
            for (var j = 0; j < response["search-results"].length; j++) {
                var items = response["search-results"][j]["items"];
                for (var i = 0; i < items.length; i++) {
                    var lat1;
                    var lon1;
                    if (items[i].hasOwnProperty("location")) {
                        lat1 = items[i].location.coordinates[1];
                        lon1 = items[i].location.coordinates[0];
                    } else if (items[i].hasOwnProperty("latitude")) {
                        lat1 = items[i].latitude;
                        lon1 = items[i].longitude;
                    } else {
                        console.log("No known location property for data source"
                                .concat(response["search-results"][j]["id"]).toString());
                        break;
                    }
                    var myLatLon = new google.maps.LatLng(lat1,lon1);
                    var mark = new google.maps.Marker({
                        position: myLatLon,
                        map: map,
                        title: items[i].description,
                        animation: google.maps.Animation.DROP,
                        chicartoItem: items[i],
                        chicartoItemType: response["search-results"][j]["id"]
                                                        });
                    mark.addListener("click",function() {
                      var infoWindow = new google.maps.InfoWindow();
                      infoWindow.setContent(itemToHTML(this.chicartoItem,this.chicartoItemType));
                      infoWindow.open(map,this);
                    });
                    bounds.extend(mark.getPosition());
                }
                if (items.length > 0) {
                  map.fitBounds(bounds);
                }
            }
          });
      }
}

//Takes an item from the search results array and transforms it into HTML for the info box
function itemToHTML(item,type) {

  // console.log(item);
  // console.log(type);

  var theString = "<p style=\"color: black;\">"
  switch (type) {
    case 1:
      var date = new Date(item["date"]);
      theString +=    "<u>Crime</u>" + "<br/>" +
                      item["description"] + "<br/>" +
                      item["location_description"] + "<br/>" +
                      dateToString(date) +
                      "</p>";
    break;
    case 2:
      var date = new Date(item["violation_date"]);
      theString +=    "<u>Building Violation</u>" + "<br/>" +
                      item["address"] + "<br/>" +
                      item["inspection_category"] + " (" + item["inspection_status"] + ")<br/>" +
                      dateToString(date) + "<br/>" +
                      item["violation_ordinance"] +
                      "</p>"
      break;
    case 3:
      theString +=    "<u>Library</u>" + "<br/>" +
                      item["name_"] + "<br/>" +
                      item["address"] + "<br/>" +
                      "Open: " + item["hours_of_operation"] + "<br/>" +
                      "<a target=\"_blank\" href=\"" + item["website"] + "\">Website</a>" + "<br/>" +
                      "Phone: " + item["phone"] +
                      "</p>"
      break;
    case 4:
      theString +=    "<u>Christmas Tree Recycling Location</u>" + "<br/>" +
                      item["address"] + "<br/>" +
                      "Free mulch: " + item["free_mulch"] + "<br/>" +
                      "</p>";
      break;
    case 5:
      var creationDate   = new Date(item["creation_date"]);
      var completionDate = new Date(item["completion_date"]);
      theString +=    "<u>311 Service Request - Tree Trim</u>" + "<br/>" +
                      item["location_of_trees"] + "<br/>" +
                      item["status"] + "<br/>" +
                      "Creation date: " + dateToString(creationDate) + "<br/>" +
                      "Completion date: " + dateToString(completionDate) + "<br/>" +
                      "</p>";
      break;
    case 6:
      var creationDate   = new Date(item["creation_date"]);
      var completionDate = new Date(item["completion_date"]);
      theString +=    "<u>311 Service Request - Tree Debris</u>" + "<br/>" +
                      item["type_of_service_request"] + "<br/>" +
                      item["most_recent_action"] + "<br/>" +
                      item["status"] + "<br/>" +
                      "Creation date: " + dateToString(creationDate) + "<br/>" +
                      "Completion date: " + dateToString(completionDate) + "<br/>" +
                      "</p>";
      break;
    case 7:
      theString +=    "<u>Police Station</u>" + "<br/>" +
                      item["address"] + "<br/>" +
                      item["phone"] + "<br/>" +
                      "District: " + item["district_name"] + "<br/>" +
                      "<a target=\"_blank\" href=\"" + item["website"] + "\">Website</a>" + "<br/>" +
                      "</p>";
      break;
    case 8:
      theString +=    "<u>Park</u>" + "<br/>" +
                      item["park_name"] + "<br/>" +
                      item["street_address"] + "<br/>" +
                      "Acres: " + item["acres"] + "<br/>" +
                      "Tennis Courts: " + item["tennis_courts"] +
                      "</p>";
      break;
    case 9:
      var creationDate   = new Date(item["creation_date"]);
      var completionDate = new Date(item["completion_date"]);
      theString +=    "<u>311 Service Request - Pot Holes</u>" + "<br/>" +
                      item["type_of_service_request"] + "<br/>" +
                      "Potholes Filled on Block: " + item["number_of_potholes_filled_on_block"] + "<br/>" +
                      item["status"] + "<br/>" +
                      "Creation date: " + dateToString(creationDate) + "<br/>" +
                      "Completion date: " + dateToString(completionDate) + "<br/>" +
                      "</p>";
      break;
    case 10:
      theString +=    "<u>L Stop</u>" + "<br/>" +
                      item["station_descriptive_name"] + "<br/>" +
                      "Direction: " + item["direction_id"] + "<br/>" +
                      "</p>";
      break;
    default:
      theString +=    "Sorry, no information available." + "</p>";
      break;
  }

  return theString;
}

function dateToString(aDate) {
  return aDate.getMonth() + "/" + aDate.getDate() + "/" + aDate.getFullYear();
}


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


//Thanks to: http://stackoverflow.com/questions/979975/how-to-get-the-value-from-the-url-parameter
var QueryString = function () {
  // This function is anonymous, is executed immediately and
  // the return value is assigned to QueryString!
  var query_string = {};
  var query = window.location.search.substring(1);
  var vars = query.split("&");
  for (var i=0;i<vars.length;i++) {
    var pair = vars[i].split("=");
        // If first entry with this name
    if (typeof query_string[pair[0]] === "undefined") {
      query_string[pair[0]] = decodeURIComponent(pair[1]);
        // If second entry with this name
    } else if (typeof query_string[pair[0]] === "string") {
      var arr = [ query_string[pair[0]],decodeURIComponent(pair[1]) ];
      query_string[pair[0]] = arr;
        // If third or later entry with this name
    } else {
      query_string[pair[0]].push(decodeURIComponent(pair[1]));
    }
  }
  return query_string;
}();
