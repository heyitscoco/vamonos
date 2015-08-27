// Functions

function toggleEvents() {
	$('#filters-div').toggle('fast');
	$('#events-div').toggle('fast');
	toggleText();
}

function toggleText() {
	$('.toggle-text').toggle();
}

function syncDistanceValues(evt) {

	var value = evt.target.value;
	$('.distance').val(value);
}

function setupDraggables() {
	$('.draggable').draggable({
		appendTo: "body",
		helper: function(){
		    return $("<div style='width: 100px;\
		    					  height: 100px;\
		    					  text-align: center;\
		    					  display: flex;\
								  justify-content: center;\
								  align-items: center;\
		    					  background-color: white;\
		    					  outline: none;\
							      border: solid #9ecaed;\
							      border-radius: 50px;\
							      box-shadow: 0 0 10px #9ecaed'>\
		    					  Drag onto the agenda to add!\
		    		  </div>");
		}
	});
	$('#agenda').droppable({
		drop: handleDropEvent,
		activeClass: "active-droppable"
	});
}

function handleDropEvent(event, ui) {
	var draggable = ui.draggable;

	var eventId = draggable.attr('id');
	var tripId = $("#agenda").data("trip");

	var url = '/event/' + eventId + '/' + tripId;

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



function toggleViewPermission(evt) {
	var canView = evt.target.dataset.view;
	var friendId = evt.target.dataset.friend;
	var tripId = $("#agenda").data("trip");
	var data = {
		friendId: friendId,
		tripId: tripId,
		canEdit: 0
	};
	console.log(evt);
	if (canView === "True") { // If user was able to view, switch to not viewing & not editing
		$.post('/rm_permission', data, function(result) {
			// Update DOM images for view & edit
			$('#edit-img-' + friendId).attr('src', '/static/img/False.png');
			evt.target.src = '/static/img/False.png';

			// Update data- attributes for view & edit
			$('#edit-img-' + friendId).attr('data-edit', 'False');
			evt.target.dataset.view = 'False';
		});
	} else { // If user was unable to view, switch to viewing
		$.post('/edit_permission', data, function(result) {
			// Update the DOM image for viewing
			evt.target.src = '/static/img/True.png';

			// Update the data- attribute for viewing
			evt.target.dataset.view = 'True';
		});
	};

}

function toggleEditPermission(evt) {
	var canView = evt.target.dataset.view;
	var canEdit = evt.target.dataset.edit;
	var friendId = evt.target.dataset.friend;
	var tripId = $("#agenda").data("trip");

	if (canEdit === 'False') {
		canEdit = 1;
		// Update DOM images for view & edit
		$('#view-img-' + friendId).attr('src', '/static/img/True.png');
		$('#view-img-' + friendId).attr('data-view', 'True');
		evt.target.src = '/static/img/True.png';
		evt.target.dataset.edit = 'True';
	} else {
		canEdit = 0;
		evt.target.src = '/static/img/False.png'
		evt.target.dataset.edit = 'False';
	}

	var data = {
		friendId: friendId,
		tripId: tripId,
		canEdit: canEdit
	}

	$.post('/edit_permission', data, function() {
		console.log('did it!');
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

function formatDatetime(dtString, fmt) {

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
			"price": price,
			"sort_by": 'date'
		};		

			url = "https://www.eventbriteapi.com/v3/events/search/"

			// request events
			$.get(url, filters, function(result) {
				var events = result.events;
				$('#toggle-events').removeClass('hidden');
				// add event names to the "Nearby Events" sidebar
				if (events) {
					events.forEach(function(event) {

								if (event.logo) {
									var eventLogo = '<img src="' + event.logo.url + '" style="width: 100%">';
								} else {
									var eventLogo = '';
								}
								var eventHTML = '<div>' + eventLogo +
													'<h5>' + event.name.text + '</h5>\
													<div>' + moment(new Date(event.start.local)).format('dddd M/D, h:mm a') + '</div>\
													<hr>\
												</div>';
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
										.text("No events could be found. Try using fewer filters!");
					$("#events-list").append(notification);
				};

				setupDraggables();
				$('#loading-img').addClass('hidden');
				$('#events-list').removeClass('hidden');
			});

	});
}
