//API handling

$('.call-api').click(apiCall);

function generateURL() {
    var url = "http://reachoutapi.herokuapp.com/resources?";

    if (_city) {
        url += "city=" + _city + "&";
    }
    if (_state) {
        url += "state=" + _state + "&";
    }
    url += "keywords=" + getKeywords();

    
    console.log(url);
    return url;
}

function api() {
    $.get(url, function (data) {
        console.log(data);
        $("#result-data").val(data.name);
        console.log(_city + " " + _state)
        console.log(getKeywords());
        console.log(url);
    });
}


function getKeywords() {
    var words = $('#keywords').val().toLowerCase();
    var arr = words.split(" ");
    var paraSting = "";
    for (var i = 0; i < arr.length; i++) {
        paraSting += arr[i] + ",";
    }
    return paraSting.substring(0, paraSting.length - 1);
}



var refcard = $('.reference-card');

function apiCall() {
    var url = generateURL();
    console.log("call apicall");
    console.log(url);
    $.ajax({
        url: url
    }).then(function (data) {
        $('.spinner').addClass('display-none');
        console.log(data)
        //Check if there is no data
        if(data.name === null || data.length == 0){
            console.log("no data");
            $('#result-data').append($('.no-data'));
            return;
        }
        for (var i = 0; i < data.length; i++) {
            var data_obj = data[i];
            var card = refcard.clone();
            console.log(card);
            console.log(data_obj.name);
            console.log(data_obj.description);
            $(card).find('.place-name').text(data_obj.name);

            $(card).find('.place-description').text(data_obj.description);

            var number_list = $(card).find('.phone-number-list');
            if (data_obj.phone_numbers.length == 0) {
                $(number_list).remove();
            }
            //Numbers
            for (var j = 0; j < data_obj.phone_numbers.length; j++) {
                var phone_number_obj = data_obj.phone_numbers[j];
                var p = $(card).find('.phone-number-object');
                $(card).find('.phone-number').text(phone_number_obj.number);
                $(p).attr('href', 'tel:' + phone_number_obj.number);
            }

            //Addresses
            var addresses = $(card).find('.address-list');
            if (data_obj.physical_locations.length == 0) {
                $(addresses).remove();
            }
            for (var k = 0; k < data_obj.physical_locations.length; k++) {
                var physical_locations_obj = data_obj.physical_locations[k];
                $(addresses).text(physical_locations_obj.name + " " + physical_locations_obj.location[0].city + ", " + physical_locations_obj.location[0].state);
            }

            //Websites
            var website_list = $(card).find('.website-list');
            if (data_obj.websites.length == 0) {
                $(website_list).remove();
            }
            for (var l = 0; l < data_obj.websites.length; l++) {
                var website = data_obj.websites[l];
                $(website_list).find('.website-link').attr('href', website)
                $(website_list).find('.website-text').text(website);
            }

            $('.card-columns').append(card);
        }
    });
}