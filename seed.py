from model import User, Trip, Permission, connect_to_db, db
from server import app

from datetime import datetime


def load_users():
	"""Load carolyn & balloonicorn into database"""

	carolyn = User(first_name="Carolyn",
				   last_name="Lee",
				   email="carolyn.lee@yale.edu",
				   password="secret"
				   )

	balloonicorn = User(first_name="Balloon",
				   last_name="iCorn",
				   email="balloonicorn@unicorn.org",
				   password="hackbright"
				   )

	db.session.add(carolyn)
	db.session.add(balloonicorn)

	db.session.commit()


def load_trips():
	"""Load carolyn's vacation into database"""

	start_date = datetime(2015, 12, 20)
	end_date = datetime(2016, 1, 5)

	trip = Trip(admin_id=1,
				title="My Trip!",
				destination="New Orleans",
				start_date = start_date,
				end_date = end_date
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



if __name__ == "__main__":
    connect_to_db(app)

    load_users()
    load_trips()
    load_permissions()
    print "Database is populated."