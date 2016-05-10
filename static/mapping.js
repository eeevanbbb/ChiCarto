function initMap() {
    var myLatLng = {lat: 41.8781, lng: -87.6298};
    // Create a map object and specify the DOM element for display.

    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 4,
        center: myLatLng
                                  });

    /**var json_file = [{"longitude": -87.5, "latitude": 42, "description":
                     "test point 1"},
                     {"longitude": -87.0, "latitude": 41.5, "description":
                      "test point 2"}];**/

        searchID = QueryString.s;
        if (searchID) {
          httpGetAsync("http://127.0.0.1:5000/search-results/"+searchID, function(response) {
            var i;
            response = JSON.parse(response);
                var len = Object.keys(response["search-results"]).length;
                for(i = 0; i < len; i++)
                {
                    var lat1 = response["search-results"][i].latitude;
                    var lon1 = response["search-results"][i].longitude;
                    var myLatLon = new google.maps.LatLng(lat1,lon1);
                    var mark = new google.maps.Marker({
                        position: myLatLon,
                        map: map,
                        title: response["search-results"][i].description
                                                        });
                }
          });
      }
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
