// function findFriend(evt) {

// 	evt.preventDefault();
// 	var email = { email: $("#email").val() };
// 	console.log(email)
// 	$.post("/find_user", email, function(result) {
// 		alert(result);
// 	})
// }

// $("#find-friend").on("click", findFriend);



// https://www.eventbriteapi.com/v3/events/search/?token=CW5KKNUFU6LD7C7JKBRA&venue.city=san+francisco

function getEvents() {

	var data = { "venue.city": "san+francisco", "token": "CW5KKNUFU6LD7C7JKBRA"};
	console.log(data)
	url = "https://www.eventbriteapi.com/v3/events/search/"

	$.get(url, data, function(result) {
		console.log(result);
	})
}

$("#boston").on("click", getEvents);