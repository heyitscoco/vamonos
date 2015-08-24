// Functions

function toggleEvents() {
	$('#filters-div').toggle('fast');
	$('#events-div').toggle('fast');
	toggleText();
}

function toggleText() {
	console.log('Toggling Text');
	$('.toggle-text').toggle();
}

function syncDistanceValues(evt) {

	var value = evt.target.value;
	$('.distance').val(value);
}

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

	var url = '/add_event/' + eventId + '/' + tripId;

	// Add the event to the DB and the DOM
	$.get(url, function(result) {

		var eventObj = JSON.parse(result).event;
		var userObj = JSON.parse(result).user;

		// Define the list item
		var eventListItem = $('<div>')
							.addClass('event')
							.attr('id', 'event-list-item-' + eventObj.eventId)

		// Create the list item
		var selector = '#day' + eventObj.dayId + '-events';
		$(selector).append(eventListItem);


		// get the google API token
		$.get('/google_token', function(result) {

			var googleToken = JSON.parse(result).googleToken;
			
			if (userObj.admin) {
				var deleteEventHTML = '<form action="/rm_event" method="POST" style="display: inline-block">\
											<label>\
												<input type="hidden" name="event_id" value="' + eventObj.eventId + '">\
											</label>\
											<label>\
												<input type="hidden" name="trip_id" value="' + tripId +'">\
											</label>\
											<label>\
												<input type="submit" value="" class="icon delete-btn edit-perms btn btn-default btn-xs">\
											</label>\
										</form>';
			} else {
				var deleteEventHTML = '';
			};

			if (eventObj.url) {
				var eventbriteButtonHTML = '<a href=' + eventObj.url + ' target="_blank"data-toggle="tooltip" title="View on Eventbrite">\
																			<img src="/static/img/eventbrite.png" class="icon">\
																		</a>'
			} else {
				var eventbriteButtonHTML = ''
			};
			

			var eventHTML = '<button type="button"\
									class="info-btn icon btn btn-info btn-xs"\
									data-toggle="modal"\
									data-target="#event'+ eventObj.eventId +'">\
							</button>' + eventObj.title +

							'<!-- Event Details Modal -->\
							<div id="event' + eventObj.eventId +'" class="modal fade" role="dialog">\
								<div class="modal-dialog">\
									<!-- Modal content-->\
							    	<div class="modal-content my-modal">\
							    		<div class="modal-header centered">\
							    			<button type="button" class="close" data-dismiss="modal">&times;</button>\
							        		<h4 class="modal-title">' + eventObj.title + '</h4>\
							        		<h5>' + eventObj.address + '</h5>\
							        		<h5>' + eventObj.start + '\
							      				- ' + eventObj.end + '\
							      			</h5>\
							      		</div>\
							      		<div class="modal-body centered">\
						      			<!-- Event details -->\
							      			<div>\
							      				<p>'+ eventObj.description +'</p>\
								      		</div>\
								      		<div class="modal-footer centered">\
								      		<div>\
									      		<h5>Attending: </h5>\
									      		<span id="fname-' + eventObj.eventId + '" class="hidden">' + userObj.fname + '</span>\
											</div>\
											<form method="POST" style="display: inline-block">\
						<!-- FIXME: this creates multiple identical IDs -->\
																		<input id="event-id" value="' + eventObj.eventId + '" type="hidden">\
						<!-- FIXME: Only one of these buttons should appear at one time-->\
																	<!-- "Attend" button -->\
																		<input id="attending-btn" type="submit" class="btn btn-info btn-sm" value="Attend">\
																	<!-- "Not Attending" button -->\
																		<input id="not-attending-btn" type="submit" class="btn btn-info btn-sm" value="Not Attending">\
																	</form>' + deleteEventHTML + eventbriteButtonHTML + '</div>\
													  		</div>\
														</div>\
													</div>\
								<!-- End Modal -->';

			$('#event-list-item-' + eventObj.eventId).html(eventHTML);
		});
	});
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

		$.post("/send_text", data);
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


function editDescription(evt) {

	console.log(evt.target.dataset);
	var eventId = evt.target.dataset.id;

	$('#old-description-' + eventId).addClass('hidden');
	$('#new-description-form-' + eventId).removeClass('hidden');
	$('#' + eventId).addClass('hidden');

}

function submitDescription(evt) {

	var eventId = evt.target.dataset.id;
	var newDescription = $('#new-description-' + eventId).val();

	// Eager update the DOM
	if (newDescription == '') { // not using strict equality, incase this is Null, etc.
		newDescription = "No description available.";
	};
	
	$('#old-description-' + eventId).text(newDescription);
	$('#old-description-' + eventId).removeClass('hidden');
	$('#new-description-form-' + eventId).addClass('hidden');
	$('#' + eventId).removeClass('hidden');

	var formInputs = {
		eventId: eventId,
		newDescription: newDescription
	};

	$.post('/new_description', formInputs);
}

function cancelDescription(evt) {

	var eventId = evt.target.dataset.id;

	$('#old-description-' + eventId).removeClass('hidden');
	$('#new-description-form-' + eventId).addClass('hidden');
	$('#' + eventId).removeClass('hidden');
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

function getEvents(evt) {
	evt.preventDefault();

	$('#loading-img').removeClass('hidden');
	$('#events-list').addClass('hidden');
	toggleEvents();

	// Get my token from the server
	$.get("/token", function (result) {
		var parsedJSON = JSON.parse(result);
		var token = parsedJSON.token

		// Get filter info from data- attributes
		var tripId = $("#agenda").data("trip");
		var latitude = $("#nearby-events").data("latitude");
		var longitude = $("#nearby-events").data("longitude");

		var trip_start = $("#agenda").data("start");
		var trip_end = $("#agenda").data("end");

		// Get filter info from #event-filters form
		var distance = $('#distance').val() || '10';
		
		var categories_array = $('#categories').val() || [];
		var categories_str = categories_array.join();

		var free = $('#price-free').prop('checked');
		var paid = $('#price-paid').prop('checked');
		var price;

		if (free && paid) {
			price = ''; // returns free & paid events
		} else if (free) {
			price = 'free';
		} else if (paid) {
			price = 'paid';
		} else {
			price = '';
		};

		var filters = {
			"token": token,
			"start_date.range_start": trip_start,
			"start_date.range_end": trip_end,
			"location.latitude": latitude,
			"location.longitude": longitude,
			"location.within": distance + 'mi',
			"categories": categories_str,
			"price": price 
		};		

			url = "https://www.eventbriteapi.com/v3/events/search/"

			// request events
			$.get(url, filters, function(result) {
				var events = result.events;
				$('#toggle-events').removeClass('hidden');
				// add event names to the "Nearby Events" sidebar
				if (events) {
					events.forEach(function(event) {
								var eventHTML = '<div>\
													<h5>' + event.name.text + '</h5>\
													<div>' + new Date(event.start.local) + '</div>\
													<hr>\
												</div>'


								var nameLink = $('<a>')
									.attr('id', event.id)
									.addClass('draggable')
									.addClass('event-listing')
									.attr('href', event.url)
									.attr('target', "_blank")
									.attr('style', 'display:block')
								$("#events-list").append(nameLink);

								$('#' + event.id).html(eventHTML);
					});
				} else {
					// FIXME: WHAT DOES THIS DO?
					var notification = $('div')
										.text("No events could be found. Try using fewer filters!")
					$("#events-list").append(notification);
				};

				setupDraggables();
				$('#loading-img').addClass('hidden');
				$('#events-list').removeClass('hidden');
			});

	});
}
