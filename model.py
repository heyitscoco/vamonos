from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

########################################################################
# Model definitions

class User(db.Model):
	""" A class for users in the sqlite3 database"""

	__tablename__ = "Users"

	user_id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(30), nullable=False)
	last_name = db.Column(db.String(30), nullable=False)
	email = db.Column(db.String(100), nullable=False, unique=True)
	password = db.Column(db.String(30), nullable=False)
	
	def __repr__(self):
		return "< User ID: %d, NAME: %s >" %(self.user_id, self.first_name)

	@classmethod
	def authenticate(cls, email, password):
		"""Looks up user by email and password.

		If user is found, returns user.
			>>> User.authenticate("balloonicorn@unicorn.org", "hackbright")
			[< User ID: 2, NAME: Balloon >]

		If no such user is found, returns None.
			>>> print User.authenticate("none@email.com", "none")
			None
		"""

		# check for email/password in DB
		found_users = cls.query.filter_by(email=email, password=password).all()

		if found_users:
			return found_users[0]
		else:
			return None


class Trip(db.Model):

	__tablename__ = "Trips"

	trip_id = db.Column(db.Integer, primary_key=True)
	admin_id = db.Column(db.Integer,
						 db.ForeignKey('Users.user_id'),
						 nullable=False
						 )
	title = db.Column(db.String(100), nullable=True)
	destination = db.Column(db.String(100), nullable=False) # This shouldn't be a string
	start_date = db.Column(db.DateTime, nullable=False)
	end_date = db.Column(db.DateTime, nullable=False)


	# Do we want to set up backrefs between trips and users?

	def __repr__(self):
		return "< Trip ID: %d ADMIN: %s TITLE: %s >" % (self.trip_id, self.admin_id, self.title)

class Permission(db.Model):

	__tablename__ = "Permissions"

	perm_id = db.Column(db.Integer, primary_key=True)
	trip_id = db.Column(db.Integer,
						db.ForeignKey('Trips.trip_id'),
						nullable=False
						)
	user_id = db.Column(db.Integer,
						db.ForeignKey('Users.user_id'),
						nullable=False
						)
	can_view = db.Column(db.Boolean, nullable=False)
	can_edit = db.Column(db.Boolean, nullable=False)

	user = db.relationship(
				'User',
				backref=db.backref('permissions', order_by=trip_id)
				)

	trip = db.relationship(
				'Trip',
				backref=db.backref('permissions', order_by=trip_id)
				)

	def __repr__(self):
		return "< Permission ID: %d TRIP: %d USER: %d Edit: %r >" % (self.perm_id, self.trip_id, self.user_id, self.can_edit)

########################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travelapp.db'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."

    # db.create_all()
    # print "DB tables built."

