//Global variables to handle pages
var current, sections;

//Global variables for location
var _city, _state;


$('.change-page-forward').click(transitionForward);
$('.change-page-back').click(transitionBackward);

function transitionForward() {
    var currentIndex = jQuery.inArray(current, sections)
    //console.log(currentIndex);

    //Error Checking
    if (currentIndex == sections.length - 1) {
        return;
    }
    var next = sections[currentIndex + 1];

    //console.log(next);
    //console.log(current);

    resetTransition(next);
    resetTransition(current);
    $(current).addClass('transitionLeft');
    $(next).addClass('transitionMiddle');
    current = next;
}

function transitionBackward() {
    var currentIndex = jQuery.inArray(current, sections)
    if (currentIndex === 0) {
        return;
    }
    //console.log(currentIndex);
    var previous = sections[currentIndex - 1];

    console.log(previous);
    //console.log(current);
    resetTransition(previous);
    resetTransition(current);
    $(previous).addClass('transitionMiddle');
    $(current).addClass('transitionRight');
    current = previous;
}

// Document is ready
$(document).ready(function () {
    //Initial load of the sections
    sections = $('section');
    //console.log(sections);
    current = sections[0];
});

function resetTransition(elem) {
    $(elem).removeClass('transitionInital');
    $(elem).removeClass('transitionLeft');
    $(elem).removeClass('transitionMiddle');
    $(elem).removeClass('transitionRight');
}

//Zip code page
$('#change-zip').click(cancelZip);

//Zip code target
$('#zip').on('input', function () {
    if ($("#zip").val().length == 5) {
        console.log($("#zip").val());
        var location = getZip($("#zip").val());
    }
});

function changeZipView(location){
    $('#city-state-display').removeClass('display-none');
    $('#zip-display').addClass('display-none');
    $('#city-state').val(location);
}


function cancelZip(){
    $('#zip-display').removeClass('display-none');
    $('#city-state-display').addClass('display-none');
    $('#zip').val('');
}




function getZip(zip) {
    var lat;
    var lng;
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({ 'address': zip }, function (results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            geocoder.geocode({ 'latLng': results[0].geometry.location }, function (results, status) {
                if (status == google.maps.GeocoderStatus.OK) {
                    if (results[1]) {
                        var loc = getCityState(results);
                        console.log(loc);
                        changeZipView(loc);
                    }
                }
            });
        }
    });
    function getCityState(results) {
        var a = results[0].address_components;
        var city, state;
        for (i = 0; i < a.length; ++i) {
            var t = a[i].types;
            if (compIsType(t, 'administrative_area_level_1'))
                state = a[i].short_name; //store the state
            else if (compIsType(t, 'locality'))
                city = a[i].long_name; //store the city
        }
        //Setting global variables
        _state = state;
        _city = city
        return (city + ', ' + state)
    }
    
    function compIsType(t, s) {
        for (z = 0; z < t.length; ++z)
            if (t[z] == s)
                return true;
        return false;
    }

}




