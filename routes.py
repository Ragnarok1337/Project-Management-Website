from main_app import app
from model import db, MyTable
from flask import render_template, redirect, url_for, flash
from datetime import datetime
from form import ContactForm, ProductForm, AddTaskForm, LoginForm
import form
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func 
from flask import jsonify, request
import json

@app.route('/') # Run the API from localhost:5000

@app.route('/login', methods=['GET', 'POST'])
def display_login():
    form = LoginForm()
    if form.validate_on_submit():
        ### USERNAME AND PASSWORD ###
        if form.username.data == 'admin' and form.password.data == '123':
            print("Login successful!")
            return redirect("/index")
        else:
            msg = "Incorrect username or password. Try again."
            form.username.data = ""
            form.password.data = ""

    return render_template("login.html", title="Login Page", content="Enter your username and password.", form=form)


@app.route('/index')
def display_home():  
    return render_template("index.html", title="Virginia Store (Index/Home page)", content="These are our products!")

@app.route('/search', methods=['GET', 'POST']) #this is the log page that will print all flash messages

## SEARCH PAGE ROUTING
def search_page():

   grouping=False

   sform = form.SearchForm()

   columns = [column.name for column in MyTable.__table__.columns]

   if request.method == 'POST':

      value=sform.value.data

      if 'search_id' in request.form:  

         records = MyTable.query.filter_by(id=int(value)).all()

      elif 'search_lname' in request.form:  

         records = MyTable.query.filter(func.lower(MyTable.lname) == value.lower()).all()

      elif 'search_country' in request.form:  

         records = MyTable.query.filter(func.lower(MyTable.country) == value.lower()).all()

      elif 'order' in request.form:  #Records ordered by last name in Ascending order

         records = MyTable.query.order_by(MyTable.lname).all()

      elif 'group' in request.form:  #group by country

         grouping=True

         records = db.session.query(MyTable.country, func.count(MyTable.id)).group_by(MyTable.country).all()

      return render_template('search_result.html',title="Search result", grouping=grouping, columns=columns, records=records)

   return render_template('search.html', sform=sform, title="Search by filter", content="type a filter and click the button")

@app.route('/log')
def display_log():
    return render_template("log.html", title="Flash Logs", content="Changes made this session.")

@app.route('/report')
def display_report():
    records=MyTable.query.all()
    return render_template('report.html', title="Reports Page", content="View current orders here!", records=records)

@app.route('/order', methods=['GET','POST'])
def display_order():
    form = AddTaskForm()
    if form.validate_on_submit():
        with app.app_context():
            try:
                t = MyTable(fname=form.fname.data, lname=form.lname.data, gender=form.gender.data, country=form.country.data, date=datetime.utcnow())
                country=form.country.data,
                db.session.add(t)
                db.session.commit()
                print("Table created and record added successfully!")
            except Exception as e:
                print("Error occured while attempting to add record to table.. >:[")
                db.session.rollback()
        return redirect(url_for('display_report'))

    return render_template("order.html", form=form, title="Order Page", content="Enter your information to place order!")

@app.route('/customer', methods=['GET','POST'])
def display_customer():
    form = ContactForm()
    msg = ""

    if form.validate_on_submit():
        print("Form Submitted!")
        name = form.fname.data + " " + form.lname.data
        email = form.email.data
        msg=f"Thank you {name}. We will send a confirmation email to {email}"
        
    return render_template("customer.html", title="Customer Info Page!", content="Enter customer information on this page.", form=form, msg=msg)

@app.route('/products', methods=['GET','POST'])
def display_products():
    form = ProductForm()
    
    msg = "Test"
    if form.validate_on_submit():
        print("Form Submitted!")
        print("Product Ordered: ", form.product.data, "Color Choice: ", form.color.data)
        product = form.color.data + " " + form.product.data
        msg= f"You ordered 1 {product}. Shipping will take 5-7 business days!"
       
    
    return render_template("products.html", title="Product Info Page!", content="Order products on this page.", form=form, msg=msg)