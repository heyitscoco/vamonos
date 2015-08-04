from model import User, Trip, Permission, Event, connect_to_db, db
from server import app

from datetime import datetime


def load_users():
	"""Load carolyn & balloonicorn into database"""

	carolyn = User(fname="Carolyn",
				   lname="Lee",
				   email="carolyn.lee@yale.edu",
				   password="secret"
				   )

	balloonicorn = User(fname="Balloon",
				   lname="iCorn",
				   email="balloonicorn@unicorn.org",
				   password="secret"
				   )

	db.session.add(carolyn)
	db.session.add(balloonicorn)

	db.session.commit()


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

	db.session.commit()


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

	db.session.commit()


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

	db.session.commit()

def load_friendships():
	"""Load the friendship between Balloonicorn & Carolyn"""

	friendship = Friendship(
							)


#####################################################################
# Main Block

if __name__ == "__main__":
    connect_to_db(app)

    load_users()
    load_trips()
    load_permissions()
    load_events()
    load_friendships()

    print "Database is populated."