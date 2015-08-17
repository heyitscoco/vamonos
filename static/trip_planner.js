// Functions
function setupDraggables() {
	$('.draggable').draggable({
		helper: 'clone'
	});
	$('#agenda').droppable({
		drop: handleDropEvent
	});
}

function handleDropEvent(event, ui) {
	var draggable = ui.draggable;

	var eventId = draggable.attr('id');
	var tripId = $("#agenda").data("trip");

	console.log('eventId: ' + eventId);
	var url = '/add_event/' + eventId + '/' + tripId;

	$.get(url, function() {
		console.log('It worked! Your event has been added.');
	});


}

function setupTooltips() {
	$(".delete-btn").attr("data-toggle", "tooltip")
					.attr("title", "Delete");

	$(".edit-span").attr("data-toggle", "tooltip") // this goes on the span (not the button) so that the button can say data-toggle="tooltip"
					.attr("title", "Edit");

	$(".view-btn").attr("data-toggle", "tooltip")
					.attr("title", "View");				
}

function toggleTooltip() {
    $('[data-toggle="tooltip"]').tooltip(); 
}

function sendReminders() {
	var today = newDate();
	var startDateString = $('#trip-date-details').data('start-date');
	var startDate = newDate(startDateString);
	var tripId = $("#agenda").data("trip");

	var dayBeforeStartDate = newDate();
	dayBeforeStartDate.setDate(startDate.getDate() - 1);

	if (today.valueOf() === dayBeforeStartDate.valueOf()) {
		data = { 'tripId': tripId };

		$.post("/send_text", data, function(result){
			console.log(result);
		});
	};

	function newDate(dateString) {

		if (dateString) {
			var date = new Date(dateString);
		} else {
			var date = new Date();
		};

		date.setHours(0, 0, 0, 0);
		return date;
	}
}

function getEvents() {

	$('#loading-img').removeClass('hidden');

	$.get("/token", function (result) {
		var parsedJSON = JSON.parse(result);
		var token = parsedJSON.token

		var tripId = $("#agenda").data("trip");
		var latitude = $("#nearby-events").data("latitude");
		var longitude = $("#nearby-events").data("longitude");

		var trip_start = $("#agenda").data("start");
		var trip_end = $("#agenda").data("end");

		var data = {token: token,
					"location.latitude": latitude,
					"location.longitude": longitude,
					"location.within": "10mi",
					"start_date.range_start": trip_start,
					"start_date.range_end": trip_end
					},
			url = "https://www.eventbriteapi.com/v3/events/search/"

			// request events
			$.get(url, data, function(result) {
				var topEvents = result.events;

				// add event names to the dom
				topEvents.forEach(function(event) {
							var nameLink = $('<a>')
								.attr('id', event.id)
								.attr('class', 'draggable')
								.text(event.name.text)
								.attr('href', event.url)
								// .attr('href', "/add_event/" + event.id + "/" + tripId)
								.attr('target', "_blank")
								.attr('style', 'display: inline-block');
							$("#events-list").append(nameLink);

				});
				setupDraggables();
				$('#loading-img').addClass('hidden');
			});

	});
};

function submitViewPermission(evt) {
	evt.preventDefault();

	var tripId = $("#agenda").data("trip");
	var formInputs = { tripId: $("#agenda").data("trip"), friendId: $("#friend_id").val(), canEdit: 0 };

	$.post("/add_permission", formInputs, function (result) {
		var friendSelector = '#friend' + formInputs.friendId;
		var friend = $(friendSelector);

		friend.addClass('hidden');

	});	
}

function submitEditPermission(evt) {
	evt.preventDefault();
	var formInputs = { tripId: $("#agenda").data("trip"), friendId: $("#friend_id").val(), canEdit: 1 };

	$.post("/add_permission", formInputs, function() {
		var friendSelector = '#friend' + formInputs.friendId;
		var friend = $(friendSelector);

		if (friend.is(':hidden')) {
			friend.text('(editor)').removeClass('hidden');
		};
	});
}

function addAttendee(evt) {
	evt.preventDefault();
	var eventId = $('#event-id').val()
	var formInputs = { eventId: eventId };
	$.post('/add_attendee', formInputs, function() {
		$('#fname-' + eventId).removeClass('hidden');
	});
}

function rmAttendee(evt) {
	evt.preventDefault();
	var eventId = $('#event-id').val()
	var formInputs = { eventId: eventId };
	$.post('/rm_attendee', formInputs, function() {
		$('#fname-' + eventId).addClass('hidden');
	});
}

function generatePDF() {
	var tripId = $("#agenda").data("trip");
	var formInputs = { tripId: tripId };

	$.post("/pdf", formInputs, function (result) {
		result = JSON.parse(result);
		var filename = result.filename;
		var url = "/itinerary" + tripId;
		window.open(url, "_blank");
	})
}