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

	var url = '/add_event/' + eventId + '/' + tripId;

	$.get(url, function(result) {

		var eventObj = JSON.parse(result).event;
		var userObj = JSON.parse(result).user;

		// Define the list item
		var eventListItem = $('<li>')
							.addClass('event')
							.attr('id', 'list-item-' + eventObj.dayId)

		// Create the list item
		var selector = '#day' + eventObj.dayId + '-events';
		$(selector).text(result.status)
			.append(eventListItem);


		// get the google API token
		$.get('/google_token', function(result) {

			var googleToken = JSON.parse(result).googleToken;
			
			if (userObj.admin) {
				var deleteEventHTML = '<form action="/rm_event" method="POST" style="display: inline-block">\
											<label>\
												<input type="hidden" name="event_id" value="{{ event.event_id }}">\
											</label>\
											<label>\
												<input type="hidden" name="trip_id" value="{{ trip.trip_id }}">\
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
									style="width: 24px; height: 24px;"\
									class="info-btn icon btn btn-info"\
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
							        		<h5>{{ ' + eventObj.start + ' | datetime("time") }}\
							      				- {{ ' + eventObj.end + ' | datetime("time")  }}\
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
								<!-- End Modal -->'
			console.log('It worked! Your event has been added.');

			$('#list-item-' + eventObj.dayId).html(eventHTML);
		});

	});
	
	// location.reload();
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

function getEvents(evt) {
	evt.preventDefault();

	$('#loading-img').removeClass('hidden');

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

		var price = $('#price').prop('checked');
		if (price) {
			price = 'free';
		} else {
			price = ''; // returns free & paid events
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
				var topEvents = result.events;

				// add event names to the dom
				if (topEvents){
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
				} else{
					var notification = 
					$("#events-list").append(notification);
				}
				setupDraggables();
				$('#loading-img').addClass('hidden');
				console.log('retrieved events');
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

	console.log('Adding attendee!')
	
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
