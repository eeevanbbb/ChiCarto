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

//Thanks to create.js
//Also thanks to http://stackoverflow.com/questions/1423777/how-can-i-check-whether-a-radio-button-is-selected-with-javascript
function submitrating() {

    //create a search object
    var search = {};

    //Get id from hidden 
    var tempid = document.getElementsByName('id');
    var idd = tempid[0].value;

    //figure out which radio button is selected then pass the value
    var rating = document.getElementsByName('rating');
    var selected_value  = 0;
    for ( var i = 0; i < rating.length; i++) {
	if(rating[i].checked) {
	    selected_value = rating[i].value;
	    break;
	}
    }
    search.rating = selected_value;
    search.id = idd;
    console.log(idd); 
    console.log(search);
    httpPostAsync("/rate_search",search,function(response) {
	    console.log(response);
	   	});
    //There is still an error. id and rating get passed but
    // there is a weird 422 UNPROCESSABLE ENTITY error :(

}