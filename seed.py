from model import *
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
				   password="secret",
				   img_url="/static/img/balloonicorn.png"
				   )

	monty = User(fname="Monty",
				   lname="Python",
				   email="monty@python.com",
				   password="secret",
				   img_url="/static/img/python.gif"
				   )

	db.session.add(carolyn)
	db.session.add(balloonicorn)
	db.session.add(monty)


def load_trips():
	"""Load carolyn's vacation into database"""

	start = datetime(2015, 12, 20)
	end = datetime(2015, 12, 25)

	trip = Trip(admin_id=1,
				title="My Trip!",
				start=start,
				end=end,
				latitude='29.951066',
				longitude='-90.071532'
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


def load_days():
	"""Load all days for 'My Trip!' into the DB"""

	times = [(datetime(2015, 12, 20, 00, 00, 00), datetime(2015, 12, 20, 23, 59, 59)),
			 (datetime(2015, 12, 21, 00, 00, 00), datetime(2015, 12, 21, 23, 59, 59)),
			 (datetime(2015, 12, 22, 00, 00, 00), datetime(2015, 12, 22, 23, 59, 59)),
			 (datetime(2015, 12, 23, 00, 00, 00), datetime(2015, 12, 23, 23, 59, 59)),
			 (datetime(2015, 12, 24, 00, 00, 00), datetime(2015, 12, 24, 23, 59, 59)),
			 (datetime(2015, 12, 25, 00, 00, 00), datetime(2015, 12, 25, 23, 59, 59))
			 ]

	for i in range(6):
		day = Day(trip_id=1,
				  day_num=i+1,
				  start=times[i][0],
				  end=times[i][1]
				  )

		db.session.add(day)

	db.session.commit()



def load_events():
	"""Load one event for Carolyn's trip"""

	file = open('static/data/events.txt')

	for line in file:
		print line
		day_id, user_id, title, start, end, city = line.rstrip().split("|")

		start = datetime.strptime(start, "datetime(%Y, %m, %d)")
		end = datetime.strptime(end, "datetime(%Y, %m, %d)")
		
		event = Event(day_id=day_id,
					  user_id=user_id,
					  title=title,
					  start=start,
					  end=end,
					  city=city,
					)

		db.session.add(event)


def load_friendships():
	"""Load the friendships between Balloonicorn & Carolyn"""

	file = open('static/data/friendships.txt')

	for line in file:
		admin_id, friend_id = line.rstrip().split(",")

		friendship = Friendship(admin_id=admin_id,
								friend_id=friend_id
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
    load_friendships()
    # load_days()
    db.session.commit()
    print "Database is populated."