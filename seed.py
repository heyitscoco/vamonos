from model import User, Trip, Permission, Event, Friendship, connect_to_db, db
from server import app

from datetime import datetime


def load_users():
	"""Load carolyn & balloonicorn into database"""

	carolyn = User(fname="Carolyn",
				   lname="Lee",
				   email="carolyn.lee@yale.edu",
				   password="secret",
				   img_url="/static/img/carolyn.jpg"
				   )

	balloonicorn = User(fname="Balloon",
				   lname="iCorn",
				   email="balloonicorn@unicorn.org",
				   password="secret"
				   )

	db.session.add(carolyn)
	db.session.add(balloonicorn)


def load_trips():
	"""Load carolyn's vacation into database"""

	start = datetime(2015, 12, 20)
	end = datetime(2016, 1, 5)

	trip = Trip(admin_id=1,
				title="My Trip!",
				start = start,
				end = end,
				city = "New Orleans",
				country_code = "US",
				country_name = "United States of America"
				)

	db.session.add(trip)


def load_permissions():
	"""Load permissions for Carolyn & Balloonicorn on carolyn's vacation"""

	perm_carolyn = Permission(trip_id=1,
					   user_id=1,
					   can_view=True,
					   can_edit=True
					   )

	perm_balloon = Permission(trip_id=1,
					   user_id=2,
					   can_view=True,
					   can_edit=False
					   )

	db.session.add(perm_carolyn)
	db.session.add(perm_balloon)


def load_events():
	"""Load one event for Carolyn's trip"""

	event = Event(trip_id=1,
				  user_id=1,
				  title="Balloonicorn's Bday Bash",
				  start=datetime(2015, 12, 23),
				  end=datetime(2015, 12, 26),
				  city="New Orleans",
				  country_code="US",
				  country_name="United States of America"
				)

	db.session.add(event)


def load_friendships():
	"""Load the friendships between Balloonicorn & Carolyn"""

	friendship = Friendship(admin_id=1,
							friend_id=2
							)
	db.session.add(friendship)

	friendship = Friendship(admin_id=2,
							friend_id=1
							)
	db.session.add(friendship)
	

#####################################################################
# Main Block

if __name__ == "__main__":
    connect_to_db(app)

    load_users()
    load_trips()
    load_permissions()
    load_events()
    load_friendships(); db.session.commit()
    print "Database is populated."