from main_app import app
from model import db, Tasks, Users
from flask import render_template, redirect, url_for, flash, session, request
from datetime import datetime
from form import ContactForm, ProductForm, AddTaskForm, LoginForm
import form
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask import jsonify
from current_session import CurrentSession  as CS

# Current Session Instance

@app.route('/')  # Run the API from localhost:5000
def home():
    return redirect(url_for('display_login'))

# Index/Home Page
@app.route('/index')
def display_home():
    
    if CS.isLoggedIn():
        return redirect(url_for("display_login"))
    return render_template("index.html", title="Virginia Store (Index/Home page)", content="These are our products!", username=session.get("username"))

#Login Page
@app.route('/login', methods=['GET', 'POST'])
def display_login():
    form = LoginForm()
    msg = ""
    
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        if CS.authenticate(username, password):
            session["username"] = username
            print("Login successful!")
            return redirect(url_for("display_home"))
        else:
            msg = "Incorrect username or password. Try again."
            form.username.data = ""
            form.password.data = ""

    return render_template("login.html", title="Login Page", content="Enter your username and password.", form=form, msg=msg)

# Logout Routing
@app.route('/logout')
def logout():
    session.pop("username", None)
    return redirect(url_for('display_login'))

# Search Page
@app.route('/search', methods=['GET', 'POST'])
def search_page():
    if CS.isLoggedIn():
        return redirect(url_for("display_login"))

    sform = form.SearchForm()

    # Get column names for display in results
    task_columns = [column.name for column in Tasks.__table__.columns]
    user_columns = [column.name for column in Users.__table__.columns]

    if request.method == 'POST' and sform.validate_on_submit():
        value = sform.value.data
        records = []

        if 'search_title' in request.form:
            records = Tasks.query.filter(Tasks.title.ilike(f"%{value}%")).all()
        elif 'search_description' in request.form:
            records = Tasks.query.filter(Tasks.body.ilike(f"%{value}%")).all()
        elif 'search_username' in request.form:
            records = Users.query.filter(Users.username.ilike(f"%{value}%")).all()

        return render_template(
            'search_result.html',
            title="Search result",
            task_columns=task_columns,
            user_columns=user_columns,
            records=records
        )

    return render_template(
        'search.html',
        sform=sform,
        title="Search Tasks",
        content="Search through active tasks and users."
    )

# Log Page
@app.route('/log')
def display_log():
    if CS.isLoggedIn():
        return redirect(url_for("display_login"))
    return render_template("log.html", title="Flash Logs", content="Changes made this session.")

# Add Task Page - ( Only Visible To Admin & Manager Role Users )
@app.route('/add-task', methods=['GET', 'POST'])
def display_order():
    if CS.isLoggedIn():
        return redirect(url_for("display_login"))

    form = AddTaskForm()
    if form.validate_on_submit():
        with app.app_context():
            try:
                t = form.TaskTable(fname=form.fname.data, lname=form.lname.data, gender=form.gender.data, country=form.country.data, date=datetime.utcnow())
                db.session.add(t)
                db.session.commit()
                print("Table created and record added successfully!")
            except Exception as e:
                print("Error occurred while attempting to add record to table.")
                db.session.rollback()
        return redirect(url_for('display_report'))

    return render_template("order.html", form=form, title="Order Page", content="Enter your information to place order!")

# EMPLOYEES PAGE
@app.route('/employees', methods=['GET'])
def display_employees():
    if CS.isLoggedIn():
        return redirect(url_for("display_login"))

    employees = Users.query.all()
    employee_columns = [column.name for column in Users.__table__.columns]

    return render_template(
        "employees.html",
        title="Employee Info Page!",
        content="View all employee information on this page.",
        employees=employees,
        employee_columns=employee_columns
    )

# ALL TASKS PAGE
@app.route('/tasks', methods=['GET', 'POST'])
def display_tasks():
    if CS.isLoggedIn():
        return redirect(url_for("display_login"))

    tasks = Tasks.query.all()
    task_columns = [column.name for column in Tasks.__table__.columns]

    return render_template(
        "tasks.html",
        title="All Tasks Page!",
        content="View all active tasks on this page.",
        form=form,
        tasks=tasks,
        task_columns=task_columns
    )
