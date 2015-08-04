function findFriend(evt) {

	evt.preventDefault();
	var email = { email: $("#email").val() };
	console.log(email)
	$.post("/find_user", email, function (result) {
		alert(result);
	})
}

$("#find-friend").on("click", findFriend);