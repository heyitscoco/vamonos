function authenticate(evt){
	evt.preventDefault();

	login_info = $("form").serialize()

	$.post("/login", login_info, function (results) {
		alert(results);
	});
}

$('#login-submission').on('click', authenticate);