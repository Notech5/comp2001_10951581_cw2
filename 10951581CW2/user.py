#library imports
import requests
from flask import make_response, abort

#file imports
from config import db
from models import User, View, PreferredActivity, users_schema, user_schema, view_schema

#global variables
email = None
authorised = False

#----------------------------------------------------------------
#Function definitions
#----------------------------------------------------------------

#authenticator funtion
def authenticate(body):

    global authorised
    global email

    #authenticator endpoint
    AUTH_URL = "https://web.socem.plymouth.ac.uk/COMP2001/auth/api/users"

    #retrieves user input
    email = body.get("email")
    password = body.get("password")

    #prevents sending empty payloads
    if not email or not password:
        abort(400, "Email and password are required")

    #constructs payload
    payload = {
        "email": email,
        "password": password
    }

    #main function body
    try:
        
        response = requests.post(AUTH_URL, json=payload, timeout=5)
        
        #valid response
        if response.status_code == 200:

            #checks response true or false
            auth_response = response.json()
            verified = auth_response[1]

            #sets global variable
            if verified == "True":

                authorised = True
            
            #resets if user changes login
            else:

                authorised = False

            return response.json(), 200

        #don't think the authenticator actually returns anything other than JSON but i don't know that for sure so extra error handling
        if response.status_code == 401:
            abort(401, "Invalid email or password")

        abort(response.status_code, response.text)

    #internal server error
    except requests.exceptions.RequestException as e:
        abort(500, f"Auth service error: {str(e)}")

#display ProfileView view - gathers data from tables to give an overview of a user profile
def get_user_profiles():
    global authorised

    if not authorised:
        abort(404, "Resource not found")

    try:
        #fetch all rows from the view
        profiles = db.session.query(View).all()

        #activities per user
        result = {}
        for row in profiles:
            uid = row.UserID
            if uid not in result:
                result[uid] = {
                    "UserID": row.UserID,
                    "Username": row.Username,
                    "FirstName": row.FirstName,
                    "LastName": row.LastName,
                    "Email": row.Email,
                    "Age": row.Age,
                    "City": getattr(row, "City", None),
                    "Country": getattr(row, "Country", None),
                    "Activities": []
                }

            if getattr(row, "ActivityNames", None):
                activities = [a.strip() for a in row.ActivityNames.split(",")]
                #only add new activities to avoid duplicates
                for act in activities:
                    if act not in result[uid]["Activities"]:
                        result[uid]["Activities"].append(act)

        return list(result.values()), 200

    except Exception as e:
        return {"error": str(e)}, 500

#function to read all user in the users table only
def read_all():

    #retrieve state of global bool
    global authorised

    #user authorised
    if authorised:
        
        #returns whole user table
        users = User.query.all()
        return users_schema.dump(users)
    
    #user not authorised
    else:

        abort(404, "Resource not found")

#search for users by field and value
def read_one(field, value):
    global authorised
    global email

    try:
        #retrieve the user specified
        user = User.query.filter(getattr(User, field) == value).one_or_none()

        if authorised and user is None:

            abort(404, f"User with {field} '{value}' not found")

        if not authorised and uses is None:

            abort(404, f"Resource not found")

        #permission check
        if authorised or (email is not None and user.Email == email):

            return user_schema.dump(user)

        #not authorised
        else:
            abort(404, "Resource not found")

    #invalid field
    except AttributeError:
        abort(400, f"Field '{field}' is invalid")

    #database error
    except Exception as e:
        
        abort(500, f"Database error: {str(e)}")
        

#update a user by a specific field
def update(field, value, body):

    global authorised
    global email

    try:
        #find user
        user = User.query.filter(getattr(User, field) == value).one_or_none()

        if user is None:
            abort(404, f"User with {field} '{value}' not found")

        #permission check
        if not authorised and user.Email != email:
            abort(403, "Forbidden")

        #update user fields
        updated_user = user_schema.load(
            body,
            instance=user,
            session=db.session,
            partial=True  # allows partial updates
        )

        db.session.commit()

        #activittyID handling
        activity_ids = body.get("ActivityIDs")
        if activity_ids is not None:
            #avoid duplicates
            # remove existing preferences
            PreferredActivity.query.filter_by(UserID=user.UserID).delete()

            # add new ones
            for act_id in activity_ids:
                pa = PreferredActivity(UserID=user.UserID, ActivityID=act_id)
                db.session.add(pa)

            db.session.commit()

        return user_schema.dump(updated_user), 200

    except AttributeError:
        abort(400, f"Field '{field}' is invalid")

    except Exception as e:
        abort(500, f"Database error: {str(e)}")

    #invalid field provided
    except AttributeError:

        abort(400, f"Field '{field}' is invalid")
    
    #internal server error
    except Exception as e:
    
        abort(500, f"Database error: {str(e)}")

#delete user by specific field
def delete(field, value): #extra check to prevent accidental deletion
    
    #check global email bool
    global email
    global authorised

    #user authorised
    try:
        
        #find user
        user = User.query.filter(getattr(User, field) == value).one_or_none()

        #user does not exist
        if user is None:
            abort(404, f"User with {field} '{value}' not found")

        #admins can delete any profile and non-admins can only delete their own
        if authorised or user.Email == email:
            
            db.session.delete(user)
            db.session.commit()
            return make_response(f"User with {field} '{value}' successfully deleted", 200)

        #user not authorised
        else:
            
            abort(404, "Resource not found")

    #invalid field
    except AttributeError:
        
        abort(400, f"Field '{field}' is invalid")
    
    #internal server error
    except Exception as e:
        
        abort(500, f"Database error: {str(e)}")

#create a new user
def create(user):

    #used for existing checks
    username = user.get("UserName")
    userid = user.get("UserID")
    emailCheck = user.get("Email")

    #checks for existting users with attributes
    existing_username = User.query.filter(User.UserName == username).one_or_none()
    existing_id = None

    existing_email = User.query.filter(User.Email == emailCheck).one_or_none()

    #user already exists
    if userid is not None:
        
        existing_id = User.query.filter(User.UserID == userid).one_or_none()

    #free to use id and username
    if existing_username is None and existing_id is None and existing_email is None:
        # create user
        new_user = user_schema.load(user, session=db.session)
        db.session.add(new_user)
        db.session.commit()

        # handle ActivityIDs input (optional)
        activity_ids = user.get("ActivityIDs", [])
        for act_id in activity_ids:
            pa = PreferredActivity(UserID=new_user.UserID, ActivityID=act_id)
            db.session.add(pa)
        db.session.commit()

        return user_schema.dump(new_user), 201

    #username already taken
    elif existing_username is not None:
        
        abort(409, f"User with username '{username}' already exists")

    elif existing_email is not None:
        
        abort(409, f"User with email '{emailCheck}' already exists")

    #user with id already exists
    else:
        
        abort(409, f"User with user ID '{userid}' already exists")
