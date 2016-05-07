    function initMap() {
    var myLatLng = {lat: 41.8781, lng: -87.6298};

    // Create a map object and specify the DOM element for display.            

    var map = new google.maps.Map(document.getElementById('map'), {
            center: myLatLng,
            scrollwheel: true,
            zoom: 13
        });

    // Create a marker and set its position.                                   

    var marker = new google.maps.Marker({
            map: map,
            position: myLatLng,
            title: 'Hello World!'
        });
}