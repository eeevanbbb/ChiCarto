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
          httpGetAsync("http://127.0.0.1:5000/search-results/"+searchID, function(response) {
            var bounds = new google.maps.LatLngBounds();
            response = JSON.parse(response);
            var items = response["search-results"][0]["items"];
            for (var i = 0; i < items.length; i++) {
                var lat1 = items[i].latitude;
                var lon1 = items[i].longitude;
                var myLatLon = new google.maps.LatLng(lat1,lon1);
                var mark = new google.maps.Marker({
                    position: myLatLon,
                    map: map,
                    title: items[i].description,
                    animation: google.maps.Animation.DROP,
                    chicartoItem: items[i]
                                                    });
                mark.addListener("click",function() {
                  var infoWindow = new google.maps.InfoWindow();
                  infoWindow.setContent(itemToHTML(this.chicartoItem));
                  infoWindow.open(map,this);
                });
                bounds.extend(mark.getPosition());
            }
            if (items.length > 0) {
              map.fitBounds(bounds);
            }
          });
      }
}

//Takes an item from the search results array and transforms it into HTML for the info box
function itemToHTML(item) {
  //FIXME: Better way of detecting which type of search this was

  var theString = ""
  if (item["description"]) {
  var date = new Date(item["date"]);
  theString +=    "<p>" +
                  item["description"] + "<br/>" +
                  item["location_description"] + "<br/>" +
                  dateToString(date) +
                  "<p>";
  } else if (item["address"]) {
    var date = new Date(item["violation_date"]);
    theString +=    "<p>" +
                    item["address"] + "<br/>" +
                    item["inspection_category"] + " (" + item["inspection_status"] + ")<br/>" +
                    dateToString(date) + "<br/>" +
                    item["violation_ordinance"]
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
