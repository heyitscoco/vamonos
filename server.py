from flask import Flask, redirect, render_template, flash, session, request
from model import User, Trip, Permission, db, connect_to_db
from datetime import datetime


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
		session["user_id"] = user.user_id
		url = "/user%d/trips" % (user.user_id)
		session_msg = "Session: %s" %(session)
		flash(session_msg)
		return redirect(url)
	else:
		flash("Your information could not be found in the system.")
		return redirect("/")


@app.route("/user<int:user_id>/trips")
def trips(user_id):
	"""Displays all of a user's trips"""

	permissions = Permission.query.filter_by(user_id=user_id).all()

	trip_tuples = [(perm.trip.title, perm.trip.trip_id) for perm in permissions]

	return render_template("trips.html", user_id=user_id, trip_tuples=trip_tuples)


@app.route("/user<int:user_id>/trip<int:trip_id>")
def my_trip(user_id, trip_id):
	"""Displays trip planning page"""

	return render_template("planner.html", user_id=user_id, trip_id=trip_id)

@app.route("/create_trip")
def new_trip():
	"""Displays a form for creating a new trip"""

	#TODO: Get user_id from SESSION
	user_id = session["user_id"]
	return render_template("create_trip.html", user_id=user_id)


@app.route("/create_trip", methods=["POST"])
def create_trip():
	"""Adds a trip to the database"""

	title = request.form.get("title")
	city = request.form.get("city")

	start_raw = request.form.get("start")
	start = datetime.strptime(start_raw, "%Y-%m-%d")

	end_raw = request.form.get("end")
	end = datetime.strptime(end_raw, "%Y-%m-%d")

	# Add trip to DB
	trip = Trip(admin_id=session["user_id"],
				title=title,
				start=start,
				end=end,
				city=city
				)
	db.session.add(trip)
	db.session.commit() # Commit here so that you can retrieve the trip_id!

	# Add permissions to DB
	perm = Permission(trip_id=trip.trip_id,
					  user_id=session["user_id"],
					  can_view=True,
					  can_edit=True
					  )
	db.session.add(perm)
	db.session.commit()

	flash("Your trip has been created!")

	return render_template("trip_planner.html", trip_id=trip.trip_id)


if __name__ == "__main__":
	connect_to_db(app)
	app.run(debug=True)