from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app=Flask(__name__, static_folder="Styles")
app.config['SECRET_KEY']='FUCK'

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabase.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

print("Database URI: ", app.config["SQLALCHEMY_DATABASE_URI"])

db=SQLAlchemy(app)

class MyTable(db.Model):
    __tablename__ = "MyTable"
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(2))
    country = db.Column(db.String(100))
    date = db.Column(db.Date, nullable = False)

    # 'repr' method represents how one object of this table will look like
    def __repr__(self):
        return f"First Name: {self.fname}, Date: {self.date} "



from routes import *
if __name__ == '__main__':
    with app.app_context():
        
        db.create_all()
    app.run(debug=True)
    