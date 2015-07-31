from flask import Flask, render_template, session, request
from model import User, Trip, Permission

app = Flask(__name__)
app.secret_key = "most_secret_key_EVER!!!!!!!"

@app.route("/")
def home():
	return render_template('home.html')

@app.route("/login", methods=['GET', 'POST'])
def login_page():

	email = request.form['email']
	password = request.form['password']
	
	user = User.authenticate(email, password) # correct email / wrong pswd?

	if user:
		session["user_id"] = user.user_id
		session["first_name"] = user.first_name

	else:
		# handle failed login attempts
		return "Not found!"


@app.route("/authenticate")
def authenticate():
	"""Checks database for a given email & password. Returns boolean."""
	
	QUERY = "SELECT "


@app.route("/user<int:user_id>/trip<int:trip_id>")
def my_trip(user_id, trip_id):

	


	return render_template("planner.html", user_id=user_id, trip_id=trip_id)




if __name__ == "__main__":
	app.run(debug=True)