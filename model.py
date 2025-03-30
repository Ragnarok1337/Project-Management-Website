from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()

class MyTable(db.Model):
    __tablename__ = 'MyTable' 
    id=db.Column(db.Integer, primary_key=True)
    fname=db.Column(db.String(100), nullable=False)
    lname=db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(2))
    country=db.Column(db.String(100))
    date=db.Column(db.Date, nullable=False)

    # repr method represents how one object of this datatable will look like
    def __repr__(self):
        return f"First Name : {self.fname}, Date: {self.date}"