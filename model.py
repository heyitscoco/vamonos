from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime, timedelta
import pytz

from reportlab.pdfgen import canvas

from twilio.rest import TwilioRestClient
from os import environ

<<<<<<< HEAD
PORT = environ.get('PORT', 5000)
=======
DATABASE_URL = environ.get("DATABASE_URL",
                              "postgresql://carolynlee@localhost/vamonos")
>>>>>>> postgres

eb_token = environ['EB_PERSONAL_OAUTH']
tw_token = environ['TW_AUTH_TOKEN']
tw_sid = environ['TW_ACCOUNT_SID']
TWILIO_NUMBER = environ['TWILIO_NUMBER']
gg_browser_key = environ['GG_BROWSER_KEY']

db = SQLAlchemy()

########################################################################
# Model definitions

class User(db.Model):
	""" A class for users in the sqlite3 database"""

	__tablename__ = 'Users'

	user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	fname = db.Column(db.String(30), nullable=False)
	lname = db.Column(db.String(30), nullable=False)
	email = db.Column(db.String(100), nullable=False, unique=True)
	password = db.Column(db.String(30), nullable=False)
	img_url = db.Column(db.String(300), nullable=False, default='/static/img/avatar.png')
	phone = db.Column(db.String(12), unique=True)
	
	def __repr__(self):
		return "< User ID: %d, NAME: %s >" %(self.user_id, self.fname)

	@classmethod
	def authenticate(cls, email, password):
		"""Looks up user by email and password."""

		try:
			return cls.query.filter_by(email=email, password=password).one()

		except NoResultFound:
			return None

	@classmethod
	def get_by_email(cls, email):
		"""Looks up user by email"""

		try:
			found_user = cls.query.filter_by(email=email).one()
			return found_user

		except NoResultFound:
			return None



class Trip(db.Model):

	__tablename__ = "Trips"

	trip_id = db.Column(db.Integer,
						primary_key=True,
						autoincrement=True
						)
	admin_id = db.Column(db.Integer,
						 db.ForeignKey('Users.user_id'),
						 nullable=False
						 )
	title = db.Column(db.String(100))
	start = db.Column(db.DateTime, nullable=False)
	end = db.Column(db.DateTime, nullable=False)
	tz_name = db.Column(db.String(50), nullable=False)
	notification_sent = db.Column(db.Boolean, default=0, nullable=False)

	# Location details
	place_name = db.Column(db.String(100))
	latitude = db.Column(db.Float, nullable=False) # FIXME: set these to false!
	longitude = db.Column(db.Float, nullable=False) # FIXME: set these to false!
	address = db.Column(db.String(200))
	city = db.Column(db.String(60))
	country_code = db.Column(db.String(5))


	def __repr__(self):
		return "< Trip ID: %d ADMIN: %s TITLE: %s >" % (self.trip_id, self.admin_id, self.title)


	def create_days(self):
		"""Creates the appropriate number of days for this trip"""

		trip_start = self.start
		trip_end = self.end

		day_start = trip_start
		day_end = day_start + timedelta(hours=23, minutes=59)
		day_num = 1

		while day_end <= trip_end:
			day = Day(trip_id = self.trip_id,
					  day_num = day_num,
					  start=day_start,
					  end=day_end
					  )
			db.session.add(day)

			day_num += 1
			day_start += timedelta(days=1)
			day_end += timedelta(days=1)

		db.session.commit()


	def update_days(self):
		"""Adds/Removes days from the trip as necessary"""

		trip_start = self.start
		trip_end = self.end
		trip_id = self.trip_id

		day_start = trip_start
		day_end = day_start + timedelta(hours=23, minutes=59)
		day_num = 1


		# FIXME: SUCKY RUNTIME

		# Delete unnecessary days
		for day in self.days:
			if day.start < trip_start or day.start >= trip_end:
				# delete all of that day's events first, for referential integrity
				for event in day.events:
					# delete all of that event's attendances first, for referential integrity
					for att in event.attendances:
						db.session.delete(att)
					db.session.delete(event)
				db.session.delete(day)

		# Add necessary days
		while day_end <= trip_end:
			try:
				# Check for a day on this trip starting at the specified time
				day = Day.query.filter(Day.trip_id == trip_id, Day.start == day_start).one()
				day.day_num = day_num

			except NoResultFound:
				# Create the necessary day
				day = Day(trip_id=trip_id,
						  day_num=day_num,
						  start=day_start,
						  end=day_end
						  )
				db.session.add(day)

			day_num += 1
			day_start += timedelta(days=1)
			day_end += timedelta(days=1)

		db.session.commit()


	def generate_itinerary(self, filename):
		"""Generates a PDF of the itinerary"""

		# Create canvas
		my_canvas = canvas.Canvas(filename, bottomup=0)
		
		# Add trip title
		my_canvas.drawString(100, 100, self.title)

		# Add events & attendees for each day
		y = 140
		for day in self.days:
			if day.events:
				trip = day.trip
				day_start = declare_tz(day.start, trip.tz_name)
				day_start = datetime.strftime(day_start, "%b %d")
				day_header = "%s (Day %d):" % (day_start, day.day_num)

				my_canvas.drawString(100, y, day_header)
				y += 20

				for event in day.events:
					event_start = declare_tz(event.start, 'utc', result='aware')
					event_start = convert_to_tz(event_start, trip.tz_name)
					event_start = datetime.strftime(event_start, "%-I:%M %p")
					event_header = "%s - %s" % (event_start, event.title)

					my_canvas.drawString(100, y, event_header)
					y += 20

					if event.attendances:
						friend_names = []
						for att in event.attendances:
							fname = User.query.get(att.user_id).fname
							friend_names.append(fname)

						friend_names = 'Attending: ' + ' '.join(friend_names)
						my_canvas.drawString(100, y, friend_names)
						y += 20
					y += 20
				y += 20

		my_canvas.showPage
		my_canvas.save()


	def send_SMS(self, twilio_sid, twilio_token):
		"""Sends a text to the viewers of the trip"""

		if not self.notification_sent:
			numbers = []
			for perm in self.permissions:
				user = User.query.get(perm.user_id)
				if user.phone:
					numbers.append(user.phone)

			client = TwilioRestClient(twilio_sid, twilio_token)

			admin_name = User.query.get(self.admin_id).fname
			msg_body = "REMINDER: %s's trip to %s starts tomorrow!" % (admin_name, self.city)

			for number in numbers:
				message = client.messages.create(from_ = TWILIO_NUMBER,
											 	 to=number,
											 	 body=msg_body
											 	 )
			self.notification_sent = True
			db.session.commit()


class Permission(db.Model):

	__tablename__ = "Permissions"

	perm_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	trip_id = db.Column(db.Integer,
						db.ForeignKey('Trips.trip_id'),
						nullable=False
						)
	user_id = db.Column(db.Integer,
						db.ForeignKey('Users.user_id'),
						nullable=False
						)
	can_edit = db.Column(db.Boolean, nullable=False)

	# Relationships
	user = db.relationship(
				'User',
				backref=db.backref('permissions', order_by=trip_id)
				)
	trip = db.relationship(
				'Trip',
				backref=db.backref('permissions', order_by=trip_id)
				)

	def __repr__(self):
		return "< Permission ID: %s TRIP: %s USER: %s Edit: %r >" % (self.perm_id, self.trip_id, self.user_id, self.can_edit)



class Day(db.Model):

	__tablename__ = "Days"

	day_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	trip_id = db.Column(db.Integer,
						db.ForeignKey('Trips.trip_id'),
						nullable=False
						)
	day_num = db.Column(db.Integer, autoincrement=False, nullable=False)
	start = db.Column(db.DateTime, nullable=False)
	end = db.Column(db.DateTime, nullable=False)
	
	# Relationships
	trip = db.relationship(
				'Trip',
				backref=db.backref('days', order_by=start)
				)

	# def __repr__(self):
	# 	return "< Day ID: %d TRIP: %d DAY_NUM: %d >" % (self.day_id, self.trip_id, self.day_num)



class Event(db.Model):

	__tablename__ = "Events"

	event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	day_id = db.Column(db.Integer,
						db.ForeignKey('Days.day_id'),
						nullable=False
						)
	user_id = db.Column(db.Integer,
						db.ForeignKey('Users.user_id'),
						nullable=False
						)
	title = db.Column(db.String(100))
	description = db.Column(db.Text, default="No description available.", nullable=False)
	start = db.Column(db.DateTime, nullable=False)
	end = db.Column(db.DateTime, nullable=False)
	url = db.Column(db.String(300))

	# Location details
	place_name = db.Column(db.String(100))
	latitude = db.Column(db.Float)
	longitude = db.Column(db.Float)
	address = db.Column(db.String(200))
	city = db.Column(db.String(60))
	country_code = db.Column(db.String(10))

	# Relationships
	user = db.relationship(
				'User',
				backref=db.backref('events', order_by=start) # user.events returns all of the events added by a given user
				)
	day = db.relationship(
				'Day',
				backref=db.backref('events', order_by=start)
				)

	def __repr__(self):
		return "<Event ID: %d TITLE: %s>" % (self.event_id, self.title)



class Attendance(db.Model):

	__tablename__ = "Attendances"

	attendance_id = db.Column(db.Integer,
						primary_key=True,
						autoincrement=True
						)
	event_id = db.Column(db.Integer,
						 db.ForeignKey('Events.event_id'),
						 nullable=False
						 )
	user_id = db.Column(db.Integer,
						db.ForeignKey('Users.user_id'),
						nullable=False
						)
	# Relationships
	event = db.relationship('Event',
							backref=db.backref('attendances')
							)
	user = db.relationship('User',
							backref=db.backref('attendances')
							)


class Friendship(db.Model):

	__tablename__ = "Friendships"

	friendship_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	admin_id = db.Column(db.Integer,
						db.ForeignKey('Users.user_id'),
						nullable=False
						)
	friend_id = db.Column(db.Integer,
						db.ForeignKey('Users.user_id'),
						nullable=False
						)

	# Relationships
	admin = db.relationship('User',
						   primaryjoin="User.user_id == Friendship.admin_id",
						   backref=db.backref("friendships")
						   )
	
	friend = db.relationship('User',
							  primaryjoin="User.user_id == Friendship.friend_id")

	def __repr__(self):
		return "< Friendship ID: %d AdminID: %d FriendID: %d >" % (self.friendship_id, self.admin_id, self.friend_id)

########################################################################
# Helper functions

def declare_tz(dt, tz_name, result='naive'):
	"""Given a naive datetime, assigns it the given timezone

	Naive datetime -> naive UTC:
		>>> dt = datetime(2015, 12, 25)
		>>> tz_name = 'UTC'
		>>> declare_tz(dt, tz_name)
		datetime.datetime(2015, 12, 25, 0, 0)

	Naive datetime -> aware UTC:
		>>> dt = datetime(2015, 12, 25)
		>>> tz_name = 'UTC'
		>>> declare_tz(dt, tz_name, result='aware')
		datetime.datetime(2015, 12, 25, 0, 0, tzinfo=<UTC>)

	Naive datetime -> pacific:
		>>> dt = datetime(2015, 12, 25)
		>>> tz_name = 'America/Los_Angeles'
		>>> declare_tz(dt, tz_name)
		datetime.datetime(2015, 12, 25, 0, 0, tzinfo=<DstTzInfo 'America/Los_Angeles' PST-1 day, 16:00:00 STD>)
	
	Given an aware datetime:
		>>> dt = datetime(2015, 12, 25)
		>>> tz = pytz.utc
		>>> dt = tz.localize(dt)
		>>> dt
		datetime.datetime(2015, 12, 25, 0, 0, tzinfo=<UTC>)
		>>> declare_tz(dt, 'America/Los_Angeles')
		Traceback (most recent call last):
		  ...
		ValueError: Not naive datetime (tzinfo is already set)

	"""

	if tz_name.lower() == 'utc':
		utc = True
		tz = pytz.utc
	else:
		utc = False
		tz = pytz.timezone(tz_name)

	dt = tz.localize(dt)

	if utc and result == 'naive':
		# return UTC datetime as NAIVE, to be stored in the DB
		dt = dt.replace(tzinfo=None)

	return dt



def convert_to_tz(dt, tz_name, result='naive'):
	"""Given an aware datetime, converts it to the given timezone

	Aware datetime -> naive UTC:
		>>> dt = datetime(2015, 12, 25)
		>>> tz = pytz.timezone('America/Los_Angeles')
		>>> dt = tz.localize(dt)
		>>> dt
		datetime.datetime(2015, 12, 25, 0, 0, tzinfo=<DstTzInfo 'America/Los_Angeles' PST-1 day, 16:00:00 STD>)
		>>> convert_to_tz(dt, 'utc')
		datetime.datetime(2015, 12, 25, 8, 0)

	Aware datetime -> aware UTC:
		>>> dt = datetime(2015, 12, 25)
		>>> tz = pytz.timezone('America/Los_Angeles')
		>>> dt = tz.localize(dt)
		>>> dt
		datetime.datetime(2015, 12, 25, 0, 0, tzinfo=<DstTzInfo 'America/Los_Angeles' PST-1 day, 16:00:00 STD>)
		>>> convert_to_tz(dt, 'utc', result='aware')
		datetime.datetime(2015, 12, 25, 8, 0, tzinfo=<UTC>)

	Aware datetime -> pacific:
		>>> dt = datetime(2015, 12, 25)
		>>> tz = pytz.utc
		>>> dt = tz.localize(dt)
		>>> dt
		datetime.datetime(2015, 12, 25, 0, 0, tzinfo=<UTC>)
		>>> convert_to_tz(dt, 'America/Los_Angeles')
		datetime.datetime(2015, 12, 24, 16, 0, tzinfo=<DstTzInfo 'America/Los_Angeles' PST-1 day, 16:00:00 STD>)

	Given a naive datetime:
		>>> dt = datetime(2015, 12, 25)
		>>> convert_to_tz(dt, 'UTC')
		Traceback (most recent call last):
		  ...
		ValueError: astimezone() cannot be applied to a naive datetime

	"""

	if tz_name.lower() == 'utc': # If the desired tz is UTC
		utc = True
		tz = pytz.utc
	else:
		utc = False
		tz = pytz.timezone(tz_name)

	dt = dt.astimezone(tz)

	if utc and result == 'naive':
		# return UTC datetimes as NAIVE, to be stored in the DB
		dt = dt.replace(tzinfo=None)

	return dt



def find_next_day(date):
	"""Given a datetime object, returns the following day as a datetime object
	
	Standard use case:
		>>> date = datetime(2015, 12, 23) 
		>>> find_next_day(date)
		datetime.datetime(2015, 12, 24, 0, 0)

	Leap-year:
		>>> date = datetime(2016, 02, 28)
		>>> find_next_day(date)
		datetime.datetime(2016, 2, 29, 0, 0)

	Non-leap-year:
		>>> date = datetime(2015, 02, 28)
		>>> find_next_day(date)
		datetime.datetime(2015, 3, 1, 0, 0)

	Year end:
		>>> date = datetime(2015, 12, 31)
		>>> find_next_day(date)
		datetime.datetime(2016, 1, 1, 0, 0)

	"""

	day = timedelta(days=1)
	date += day
	return date


def connect_to_db(app):
    """Connects the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    # app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)

########################################################################

if __name__ == "__main__":
	from server import app
	connect_to_db(app)
	print "Connected to DB."

