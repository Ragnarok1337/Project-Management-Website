from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, RadioField, EmailField, TextAreaField, PasswordField
from wtforms.validators import DataRequired
from model import db, Users

class AddTaskForm(FlaskForm):

    title= StringField("Title:", validators=[DataRequired()])
    body= TextAreaField("Description:", validators=[DataRequired()])
    user= SelectField("User")
    submit= SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        super(AddTaskForm, self).__init__(*args, **kwargs)
        # Populate the role field with usernames from the Users table
        self.user.choices = [(str(user.id), user.username) for user in Users.query.all()]
                             
class AddUserForm(FlaskForm):
    username= StringField("Username:", validators=[DataRequired()])
    password= StringField("Password:", validators=[DataRequired()])
    role= SelectField("Role", choices=[("Employee"),("Manager")])
    submit= SubmitField("Submit")

class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Login")

class SearchForm(FlaskForm):
    value = StringField('Enter Search Value:', validators=[DataRequired()])