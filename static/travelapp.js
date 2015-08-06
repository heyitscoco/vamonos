
function getEvents() {

	var latitude = $("#nearby-events").data("latitude")
	var longitude = $("#nearby-events").data("longitude")
	var data = {token: "6OLY723AIVYNJBX63FFX",
				sort_by: "best",
				price: "free",
				location.latitude: latitude,
				location.longitude: longitude,
				location.within: 30mi
	}
	url = "https://www.eventbriteapi.com/v3/events/search/"

	// request events
	$.get(url, data, function(result) {
		var topEvents = result.events.slice(0,15);
	

	// add event names to the dom
	topEvents.forEach(function(event) {
				var nameLink = $('<li>')
					.attr('href', event.resource_uri)
					.text(event.name.text)
				$("#" + city).append(nameLink)
			})
	});
}

$(document).on("ready", getEvents)



var cities = ['Boston', 'London', 'Paris'];

// var cities = $("#event-streams").data("cities");
// console.log(cities)

function getEvents() {

	// iterate thru cities
	cities.forEach(function (city) {
		var data = { "venue.city": city,
					 "token": "6OLY723AIVYNJBX63FFX",
					 "sort_by": "best",
					 "popular": 1,
					 "price": "free"
					};
		url = "https://www.eventbriteapi.com/v3/events/search/"

		// request events for that city
		$.get(url, data, function(result) {
			var topEvents = result.events.slice(0,7);

			// add event name to the dom
			topEvents.forEach(function(event) {
				var nameLink = $('<li>')
					.attr('href', event.resource_uri)
					.text(event.name.text)
				$("#" + city).append(nameLink)
			})
		})
	});
}

$(document).on('ready', getEvents);


// - Get list of cities from Python/HTML? <-- JSON!!
// - Speed it up? Limit number of results?