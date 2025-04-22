from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, RadioField, EmailField, TextAreaField, PasswordField
from wtforms.validators import DataRequired

class AddTaskForm(FlaskForm):
    title= StringField("Title:", validators=[DataRequired()])
    body= TextAreaField("Description:", validators=[DataRequired()])
    role= SelectField("User", choices=[("Employee"),("Manager")])
    submit= SubmitField("Submit")

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