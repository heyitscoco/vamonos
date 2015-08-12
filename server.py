from flask import Flask, redirect, render_template, flash, session, request, json
from model import *
from datetime import datetime, timedelta
import geocoder
import os
import requests
import random

token = os.environ['PERSONAL_OAUTH']

app = Flask(__name__)
app.secret_key = "most_secret_key_EVER!!!!!!!"

#############################################################
# Routes

@app.route("/")
def home():
	"""Displays homepage"""

	cities = ['Boston', 'Seoul', 'London', 'Paris', 'Berlin', 'Venice', 'Stockholm']
	cities_sample = random.sample(cities, 4)


	cities_dict = {}
	for city in cities_sample:
		cities_dict[city] = city

	cities_json = json.dumps(cities_dict)
	print "\n\n",type(cities_json), cities_json,"\n\n"
	
	return render_template('home.html',
							cities=cities_sample,
							citiesJSON=cities_json)



@app.route("/token")
def return_token():
	"""Returns a jsonified version of my token"""

	token_dict = {'token': token}
	return json.dumps(token_dict)



@app.route("/login", methods=['GET'])
def login_page():
	"""Displays login page"""

	return render_template("login.html")



@app.route("/login", methods=['POST'])
def login():
	"""Logs in the user, or denies access"""

	email = request.form.get("email")
	password = request.form.get("password")
	
	user = User.authenticate(email, password)

	if user:
		session["user_id"] = user.user_id
		session["fname"] = user.fname
		return redirect("/trips")

	else:
		flash("Your information could not be found in the system. Try again or sign up!")
		return redirect("/login")



@app.route("/signup", methods=['GET'])
def signup_page():
	"""Displays signup page"""

	return render_template("signup.html")



@app.route("/signup", methods=['POST'])
def signup():
	"""Adds new user to the DB."""

	email = request.form.get("email")
	found_user = User.query.filter_by(email=email).all()

	if found_user:
		msg = "We found your email in our database. Try logging in instead!"

	else:
		# Get user info from form
		fname = request.form.get("fname")
		lname = request.form.get("lname")
		password = request.form.get("password")

		# Add user to DB
		user = User(fname=fname,
				   lname=lname,
				   email=email,
				   password=password,
				   )
		db.session.add(user)
		db.session.commit()

		msg = "Welcome, %s! You're now signed up. Log in to get started!" % (fname)
	
	flash(msg)
	return redirect("/login")



@app.route("/logout")
def logout():
	"""Logs the user out, clearing the session"""

	session.clear()
	flash("You have been successfully logged out.")
	return redirect("/")



@app.route("/user<int:user_id>/profile")
def profile(user_id):
	"""Displays a user's profile"""

	user = User.query.get(user_id)
	friends = [(friendship.friend_id, friendship.friend.fname, friendship.friend.img_url) for friendship in user.friendships]
	print friends
	return render_template("profile.html", user=user, friends=friends)



@app.route("/add_friend", methods=["POST"])
def add_friend():
	"""Adds a new friendship to the DB"""

	email = request.form.get("email")
	friend = User.get_by_email(email)

	if friend:
		# Add friendship to the DB
		friendship = Friendship(admin_id=session['user_id'],
								friend_id=friend.user_id
								)
		db.session.add(friendship)
		db.session.commit()
		msg = "You have successfully added %s to your friends!" % (friend.fname)

	else:
		msg = "We couldn't find anyone with that email in our system."

	flash(msg)

	url = "/user%d/profile" % (session['user_id'])
	return redirect(url)



@app.route("/trips")
def trips():
	"""Displays all of a user's trips"""

	if 'user_id' in session:
		user_id = session["user_id"]
		permissions = Permission.query.filter_by(user_id=user_id).all()

		trip_tuples = [(perm.trip.title, perm.trip.trip_id) for perm in permissions]

		return render_template("trips.html", user_id=user_id, trip_tuples=trip_tuples)
	
	else:
		flash("Sorry, you need to be logged in to do that!")
		return redirect("/login")


@app.route("/trip<int:trip_id>")
def trip_planner(trip_id):
	"""Displays trip planning page"""

	if 'user_id' in session:
		viewer_id = session['user_id']
		trip = Trip.query.get(trip_id)
		admin_id = trip.admin_id
		permissions = Permission.query.filter(Permission.trip_id == trip_id, Permission.user_id != admin_id).all()
		friendships = Friendship.query.filter_by(admin_id = viewer_id).all()
		friends = [(friendship.friend.fname, friendship.friend_id) for friendship in friendships]

		trip = Trip.query.get(trip_id)
		trip_start_str = datetime.strftime(trip.start, "%Y-%m-%dT%H:%M:%SZ")
		trip_end_str = datetime.strftime(trip.end, "%Y-%m-%dT%H:%M:%SZ")

		trip_start_dsply = datetime.strftime(trip.start, "%b %d, %Y")
		last_day = trip.end - timedelta(1)
		trip_end_dsply = datetime.strftime(last_day, "%b %d, %Y")


		# Pass 'can_edit' boolean into template
		user_perm = Permission.query.filter(Permission.trip_id == trip_id, Permission.user_id == viewer_id).one()

		if user_perm.can_edit:
			can_edit = True
		else:
			can_edit = False

		# Pass 'admin' boolean into template
		if viewer_id == admin_id:
			admin = True
		else:
			admin = False

		return render_template("trip_planner.html",
								trip=trip,
								trip_start_str=trip_start_str,
								trip_end_str=trip_end_str,
								trip_start_dsply=trip_start_dsply,
								trip_end_dsply=trip_end_dsply,
								permissions=permissions,
								friends=friends,
								can_edit=can_edit,
								admin=admin
								)

	else:
		flash("Sorry, you need to be logged in to do that!")
		return redirect("/login")

@app.route("/add_permission", methods=["POST"])
def add_permission():
	"""Adds a new permission to the DB"""

	# Get info from form
	trip_id = int(request.form.get("tripId"))
	friend_id = int(request.form.get("friendId"))
	can_edit = int(request.form.get("canEdit"))

	if can_edit: # can_edit was 1
		can_edit = True
	else: # can_edit was 0
		can_edit = False
	
	try:
		# Check for existing permissions, update if found
		perm = Permission.query.filter(Permission.user_id == friend_id, Permission.trip_id == trip_id).one()
		perm.can_edit = can_edit
		db.session.flush()

	except NoResultFound:
		# Add new permission to DB
		perm = Permission(trip_id=trip_id,
						  user_id=friend_id,
						  can_view=True,
						  can_edit=can_edit
						  )
		db.session.add(perm)
	db.session.commit()

	# Confirm submission
	if can_edit:
		ability = "view & edit"
	else:
		ability = "view"

	friend = User.query.get(friend_id)
	msg = "%s is now allowed to %s this trip!" % (friend.fname, ability)
	flash(msg)

	friends_dict = {}

	for friend in friends:
		friend

	return json.dumps(friends_dict) # FIXME Don't return this!



@app.route("/rm_permission", methods=["POST"])
def rm_permission():
	"""Deletes a permission from the DB"""

	# Get info from form
	friend_id = request.form.get("friend_id")
	trip_id = request.form.get("trip_id")

	# Remove permission based on info
	perm = Permission.query.filter(Permission.user_id == friend_id, Permission.trip_id == trip_id).one()

	db.session.delete(perm)
	db.session.commit()

	friend = User.query.get(friend_id)
	msg = "%s is no longer allowed to view this trip." % (friend.fname)
	flash(msg)

	return redirect("/") # FIXME Don't redirect here!



@app.route("/create_trip")
def create_trip():
	"""Displays a form for creating a new trip"""

	if 'user_id' in session:
		user_id = session["user_id"]
		return render_template("create_trip.html", user_id=user_id)

	else:
		flash("Sorry, you need to be logged in to do that!")
		return redirect("/login")



@app.route("/create_trip", methods=["POST"])
def new_trip():
	"""Adds a trip to the database"""

	# Get trip details from form
	title = request.form.get("title")

	start_raw = request.form.get("start")
	start = datetime.strptime(start_raw, "%Y-%m-%d")

	end_raw = request.form.get("end")
	end = datetime.strptime(end_raw, "%Y-%m-%d")
	end = find_next_day(end)

	destination = request.form.get("destination")

	# Get more details from geocoder
	destination = geocoder.google(destination)
	address = destination.address
	lat = destination.lat
	lng = destination.lng
	city = destination.city
	country_code = destination.country

	# Add trip to DB
	trip = Trip(admin_id=session["user_id"],
				title=title,
				start=start,
				end=end,
				latitude=lat,
				longitude=lng,
				address=address,
				city=city,
				country_code=country_code
				)
	db.session.add(trip)
	db.session.commit() # Commit here so that you can retrieve the trip_id!

	# Add admin permission to DB
	perm = Permission(trip_id=trip.trip_id,
					  user_id=session["user_id"],
					  can_view=True,
					  can_edit=True
					  )
	db.session.add(perm)

	# Add days to DB
	trip.create_days()

	db.session.commit()
	
	flash("Your trip has been created!")

	url = "/trip%d" % (trip.trip_id)
	return redirect(url)



@app.route("/edit_destination", methods=["POST"])
def edit_destination():
	"""Modifies the trip destination"""

	# Get info from form
	trip_id = int(request.form.get("tripId"))
	destination = request.form.get("destination")
	destination = geocoder.google(destination)

	# Update DB
	trip = Trip.query.get(trip_id)

	trip.address = destination.address
	trip.latitude = destination.lat
	trip.longitude = destination.lng
	trip.city = destination.city
	trip.country_code = destination.country

	db.session.commit()


	return "Did it!" # FIXME Dont return this!



@app.route("/edit_start", methods=["POST"])
def edit_start():
	"""Changes the trip start"""

	# Get info from form
	trip_id = request.form.get("trip_id")
	start_raw = request.form.get("start")
	start = datetime.strptime(start_raw, "%Y-%m-%d")

	# Update DB
	trip = Trip.query.get(trip_id)

	trip.start = start
	db.session.commit()

	msg = "Nice!"
	flash(msg)
	return msg # FIXME Dont return this!



@app.route("/edit_end", methods=["POST"])
def edit_end():
	"""Changes the trip end"""

	# Get info from form
	trip_id = request.form.get("trip_id")
	end_raw = request.form.get("end")
	end = datetime.strptime(end_raw, "%Y-%m-%d") + timedelta(1)

	# Update DB
	trip = Trip.query.get(trip_id)
	
	trip.end = end
	db.session.commit()

	return "Sweet!" # FIXME Dont return this!



@app.route("/create_event", methods=["POST"])
def create_event():
	"""Adds a new event to the DB"""

	# Get info from form
	title = request.form.get("title")
	location = request.form.get("location")
	location = geocoder.google(location)

	address = location.address
	lat = location.lat
	lng = location.lng
	city = location.city
	country_code = location.country

	start_raw = request.form.get("start")
	start = datetime.strptime(start_raw, "%Y-%m-%dT%H:%M")

	end_raw = request.form.get("end")
	end = datetime.strptime(end_raw, "%Y-%m-%dT%H:%M")

	# Determine correct day
	day = Day.query.filter(Day.start <= start, Day.end >= start).all() # FIXME: Day.trip_id == trip_id

	# Add event to DB
	if day:
		day = day[0]

		event = Event(day_id=day.day_id,
					  user_id=session['user_id'],
					  title=title,
					  start=start,
					  end=end,
					  address=address,
					  latitude=lat,
					  longitude=lng,
					  city=city,
					  country_code=country_code
					  )
		db.session.add(event)
		db.session.commit()
		msg = "Your event has been added to your agenda!"

	else: # if the event is outside the trip dates
		msg = "Event creation failed: These dates are outside the dates of your trip!"
	
	flash(msg)
	
	trip = Trip.query.get(day.trip_id)
	url = "/trip%d" % (trip.trip_id)
	return redirect(url)



@app.route("/add_event/<string:event_id>/<string:trip_id>")
def add_event(event_id, trip_id):
	"""Given an eventbrite event resource_uri, adds the event to the agenda"""

	# get event info from Eventbrite API
	event_uri = "https://www.eventbriteapi.com/v3/events/%s/?token=%s" % (event_id, token)
	event = requests.get(event_uri).json()

	venue_id = event['venue_id']
	venue_uri = "https://www.eventbriteapi.com/v3/venues/%s/?token=%s" % (venue_id, token)
	venue = requests.get(venue_uri).json()

	title = event['name']['text']
	url = event['url']

	start = event['start']['utc']
	start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ")

	end = event['end']['utc']
	end = datetime.strptime(end, "%Y-%m-%dT%H:%M:%SZ")

	place_name = venue.get('address',{}).get('name')
	address = venue['address'].get('address_1')
	city = venue['address'].get('city')
	country_code = venue['address'].get('country')
	lat = venue['latitude']
	lng = venue['longitude']

	# create the event for the DB
	trip_start = Trip.query.get(trip_id).start
	trip_end = Trip.query.get(trip_id).end

	# Determine correct day
	day = Day.query.filter(Day.trip_id == int(trip_id), Day.start <= start, Day.end >= start).all()

	# Add event to DB
	if day:
		day = day[0]
		event = Event(day_id=day.day_id,
					  user_id=session['user_id'],
					  title=title,
					  start=start,
					  end=end,
					  place_name=place_name,
					  address=address,
					  city=city,
					  country_code=country_code,
					  latitude=lat,
					  longitude=lng,
					  url=url
					  )
		db.session.add(event)
		db.session.commit()

		msg = "Your event has been added!"
	else:
		msg = "Oops! Something went wrong."
	
	url = "/trip%s" %(str(trip_id))
	return redirect(url)



@app.route("/rm_event", methods=["POST"])
def rm_event():
	"""Removes an event from the trip"""
	
	event_id = request.form.get("event_id")
	trip_id = int(request.form.get("trip_id"))

	event = Event.query.filter(Event.event_id == event_id, Day.trip_id == trip_id).first()

	db.session.delete(event)
	db.session.commit()

	msg = "You have successfully removed this event."
	flash(msg)

	url = "/trip%d" % (trip_id)
	return redirect(url)

#############################################################

if __name__ == "__main__":
	connect_to_db(app)
	app.run(debug=True)