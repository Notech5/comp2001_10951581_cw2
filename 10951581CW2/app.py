#imports
from flask import render_template
from sqlalchemy import inspect
import config
from models import User, Location, Activity, PreferredActivity

#app
app = config.connex_app
app.add_api(config.basedir / "swagger.yml")

#function to initialise database
def init_db():
    
    inspector = inspect(config.db.engine)

    #import table definitions
    models = [
        (Location, Location.__tablename__),
        (User, User.__tablename__),
        (Activity, Activity.__tablename__),
        (PreferredActivity, PreferredActivity.__tablename__),
    ]

    #check if each table exists
    for model_class, table_name in models:

        schema = model_class.__table_args__['schema']
        
        #table doesn't exist
        if not inspector.has_table(table_name, schema=schema):
            
            print(f"Creating table: {schema}.{table_name}")
            model_class.__table__.create(config.db.engine)
        
        #table already exists
        else:
        
            print(f"Table already exists: {schema}.{table_name}")

#server
@app.route("/")
def home():

    users = User.query.all()

    return render_template("home.html", users=users)

if __name__ == "__main__":
    
    with config.app.app_context():
        
        #initialise database at runtime
        init_db()

    #host 
    app.run(host="0.0.0.0", port=8000, debug=True)
