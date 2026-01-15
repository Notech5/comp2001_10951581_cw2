#imports
from datetime import datetime
import pytz
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import fields, EXCLUDE
from config import db, ma

#----------------------------------------------------------------
#Table definitions
#----------------------------------------------------------------

#user table
class User(db.Model):
    
    __tablename__ = "users"
    __table_args__ = {'schema': 'CW2'}
    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserName = db.Column(db.String(20))
    FirstName = db.Column(db.String(20))
    LastName = db.Column(db.String(20))
    Email = db.Column(db.String(30))
    Age = db.Column(db.Integer, nullable=True)
    Gender = db.Column(db.String(20), nullable=True)
    LocationID = db.Column(
    db.Integer,                     
    db.ForeignKey('CW2.locations.LocationID'),  
    nullable=False                 
    
    )
    TrailID = db.Column(db.Integer, nullable=True)

    ActivityID = db.relationship(
        "PreferredActivity",
        backref="user",
        cascade="all, delete-orphan"
    )

#locations table
class Location(db.Model):
    
    __tablename__ = "locations"
    __table_args__ = {'schema': 'CW2'}
    LocationID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    City = db.Column(db.String(100))
    Country = db.Column(db.String(60))
    Region = db.Column(db.String(100), nullable=True)
    PostalCode = db.Column(db.String(15), nullable=True)

#activities table
class Activity(db.Model):
    
    __tablename__ = "activities"
    __table_args__ = {'schema': 'CW2'}
    ActivityID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ActivityName = db.Column(db.String(100), nullable=True)

#preferredactivity table
class PreferredActivity(db.Model):
    
    __tablename__ = "preferredactivities"
    __table_args__ = {'schema': 'CW2'} 

    UserID = db.Column(
        db.Integer,
        db.ForeignKey('CW2.users.UserID'), 
        primary_key=True
    )
    
    ActivityID = db.Column(
        db.Integer,
        db.ForeignKey('CW2.activities.ActivityID'),  
        primary_key=True
    )

#view to gather data and form a substantial picture of user profiles
class View(db.Model):
    
    __tablename__ = "ProfileView"
    __table_args__ = {"schema": "CW2"}

    UserID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String)
    FirstName = db.Column(db.String)
    LastName = db.Column(db.String)
    Email = db.Column(db.String)
    Age = db.Column(db.String)
    City = db.Column(db.String)
    Country = db.Column(db.String)
    ActivityNames = db.Column(db.String)
    
#----------------------------------------------------------------
#Schema definitions
#----------------------------------------------------------------

#users
class UserSchema(ma.SQLAlchemyAutoSchema):
    
    class Meta:
    
        model = User
        load_instance = True
        sql_session = db.session
        include_fk = True
        unknown = EXCLUDE  
    
    UserID = auto_field(dump_only=True)

    

#location
class LocationSchema(ma.SQLAlchemyAutoSchema):
    
    class Meta:
    
        model = Location
        load_instance = True
        sql_session = db.session

#activities
class ActivitySchema(ma.SQLAlchemyAutoSchema):
    
    class Meta:
    
        model = Activity
        load_instance = True
        sql_session = db.session

#preferredactivities
class PreferredActivitySchema(ma.SQLAlchemyAutoSchema):
    
    class Meta:
    
        model = PreferredActivity
        load_instance = True
        sql_session = db.session
        include_fk = True

#view
class ViewSchema(ma.SQLAlchemyAutoSchema):
    
    class Meta:
    
        model = View
        load_instance = False
        sql_session = db.session

    UserID = auto_field()
    Username = auto_field()
    FirstName = auto_field()
    LastName = auto_field()
    Email = auto_field()
    Age = auto_field()
    City = auto_field()
    Country = auto_field()
    
    unkown = EXCLUDE
#----------------------------------------------------------------
#Schema instantiations
#----------------------------------------------------------------

#user
user_schema = UserSchema()
users_schema = UserSchema(many=True)

#location
location_schema = LocationSchema()
locations_schema = LocationSchema(many=True)

#activities
activity_schema = ActivitySchema()
activities_schema = ActivitySchema(many=True)

#preferredactivities
preferredactivity_schema = PreferredActivitySchema()
preferredactivities_schema = PreferredActivitySchema(many=True)

#view
view_schema = ViewSchema(many=True)
