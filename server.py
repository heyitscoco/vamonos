from flask import Flask, redirect, render_template, flash, session, request
from model import User, Trip, Permission, db, connect_to_db

app = Flask(__name__)
app.secret_key = "most_secret_key_EVER!!!!!!!"

@app.route("/")
def home():
	
	return render_template('home.html')


@app.route("/login", methods=['GET'])
def login_page():

	return render_template("login.html")


@app.route("/login", methods=['POST'])
def login():
	"""Logs in the user, or denies access"""

	email = request.form.get("email")
	password = request.form.get("password")

	user = User.authenticate(email, password)

	if user:
		print "*****USER %d*****" % (user.user_id)

		url = "/user%d/trips" % (user.user_id)
		return redirect(url)
	else:
		flash("Your information could not be found in the system.")
		return redirect("/")


@app.route("/user<int:user_id>/trips")
def trips(user_id):
	permissions = Permission.query.filter_by(user_id=user_id).all()

	trip_tuples = []

	for perm in permissions:
		trip_tuples.append((perm.trip.title, perm.trip.trip_id))

	return render_template("trips.html", user_id=user_id, trip_tuples=trip_tuples)


@app.route("/user<int:user_id>/trip<int:trip_id>")
def my_trip(user_id, trip_id):
	"""Displays trip planning page"""

	return render_template("planner.html", user_id=user_id, trip_id=trip_id)




if __name__ == "__main__":
	connect_to_db(app)
	app.run(debug=True)