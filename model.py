from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()

# Users Model
class Users(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"Username: {self.username}, Role: {self.role}"


# Tasks Model
class Tasks(db.Model):
    __tablename__ = 'Tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    body = db.Column(db.String(200), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=True)
    date_created = db.Column(db.String(8), nullable=False)
    completed = db.Column(db.Integer, default=0)

    # Relationships
    assigned_user = db.relationship('Users', foreign_keys=[assigned_to])
    creator_user = db.relationship('Users', foreign_keys=[created_by])

    def __repr__(self):
        return f"Task Title: {self.title}, Assigned To: {self.assigned_user.username if self.assigned_user else 'None'}, Created By: {self.creator_user.username if self.creator_user else 'None'}, Date Created: {self.date_created}"

