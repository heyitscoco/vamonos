// https://www.eventbriteapi.com/v3/events/search/?token=CW5KKNUFU6LD7C7JKBRA&venue.city=san+francisco

function getEvents() {

	var data = { "venue.city": "san+francisco",
				 "token": "CW5KKNUFU6LD7C7JKBRA"
				};

	url = "https://www.eventbriteapi.com/v3/events/search/"

	$.get(url, data, function(result) {
		topEvents = result.events.slice(10,30);

		topEvents.forEach(function(event) {
			var nameLink = $('<li><a>')
				.attr('href', event.resource_uri)
				.text(event.name.text)
			$("#boston-events").append(nameLink)
		})
	})
}

$(document).on("ready", getEvents);
