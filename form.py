from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, RadioField, EmailField, TextAreaField, PasswordField
from wtforms.validators import DataRequired

class ContactForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Submit',  render_kw={'class': 'btn'})

class ProductForm(FlaskForm):
    product = SelectField('Product', choices = ('Coat', 'Shirt', 'Sweater', 'Pants', 'Shorts', 'Hat'))
    color = RadioField('Color', choices=('Red', 'Blue', 'Yellow', 'Green', 'Orange', 'Purple'), validators=[DataRequired()])
    submit = SubmitField('Submit',  render_kw={'class': 'btn'})

class AddTaskForm(FlaskForm):
    fname= StringField("First name:", validators=[DataRequired()])
    lname= StringField("Last name:", validators=[DataRequired()])
    gender= RadioField("Gender:", choices=[("M","Male"), ("F","Female")])
    country= SelectField("Country", choices=[("US", "USA"), ("FR", "France"), ("UK", "England"), ("GR", "Germany")], validators=[DataRequired()])
    submit= SubmitField("Submit")

class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Login")

class SearchForm(FlaskForm):
    value = StringField('Enter Search Value:', validators=[DataRequired()])