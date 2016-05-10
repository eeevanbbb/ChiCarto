function initMap() {
    var myLatLng = {lat: 41.8781, lng: -87.6298};
    // Create a map object and specify the DOM element for display.

    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 4,
        center: myLatLng
                                  });

    /*var json_file = {[{"longitude": -87.5, "latitude": 42, "description":
                     "test point 1"},
                     {"longitude": -87.0, "latitude": 41.5, "description":
                      "test point 2"}]};*/
    var marker = new google.maps.Marker({
                                        position: myLatLng,
                                        map: map,
                                        title: 'file works'
                                        });
    var i;
        //var json_file = "/search-results/{{ search.id }}" {{ search }};
        //var len = Object.keys(json_file).length;
        for(i = 0; i < 2; i++)
        {
            var lat1 = json_file[i].latitude;
            var lon1 = json_file[i].longitude;
            var myLatLon = new google.maps.LatLng(lat1,lon1);
            var mark = new google.maps.Marker({
                position: myLatLon,
                map: map,
                title: json_file[i].description
                                                });
        }
}