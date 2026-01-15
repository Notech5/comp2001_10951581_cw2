#imports
import pathlib
import connexion
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

#working directory
basedir = pathlib.Path(__file__).parent.resolve()

#app
connex_app = connexion.App(__name__, specification_dir=basedir)
app = connex_app.app

#use ODBC driver 17 and login to server
app.config["SQLALCHEMY_DATABASE_URI"] = ("mssql+pyodbc:///?odbc_connect=""DRIVER={ODBC Driver 17 for SQL Server};""SERVER=obscured for github upload;""DATABASE=obscured for github upload;""UID=obscured for github upload;""PWD=obscured for github upload;""TrustServerCertificate=yes;""Encrypt=yes;")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#SQLAlchemy and Marshmallow instances
db = SQLAlchemy(app)
ma = Marshmallow(app)

