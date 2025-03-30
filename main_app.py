from flask import Flask
from model import db
import os

app=Flask(__name__, static_folder="Styles")
app.config['SECRET_KEY']='FUCK'

# Database Configuration
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabase.db"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Define the absolute path for the database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'mydatabase.db')

# Set the SQLAlchemy database URI to the absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print("Database URI: ", app.config['SQLALCHEMY_DATABASE_URI'])

db.init_app(app)

with app.app_context():
        db.create_all()
        print("database created")

from routes import *
if __name__ == '__main__':
    app.run(debug=True)
    