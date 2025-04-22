from main_app import app
from model import db, Tasks, Users
from flask import render_template, redirect, url_for, flash, session, request
from datetime import datetime
from form import AddTaskForm, AddUserForm, LoginForm
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
        role = CS.getRole().lower()
        username = CS.getUsername()
        content = ""
        match role:
            case "admin":
                content = "Welcome Admin! You have global superuser privileges. All actions are allowed."
            case "employee":
                content = f"Hello {username} your role is {role}, you can check your assigned tasks, and see all tasks!"
            case "manager":
                content = f"Hello {username} your role is {role}, you can see all assigned tasks, and assign tasks to employees!"
        return render_template("index.html", title="Welcome to TechHub!", content=content, CS=CS)
    return redirect(url_for("display_login"))
    

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def display_login():
    form = LoginForm()
    msg = ""
    
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        if CS.authenticate(username, password):
            session["username"] = username
            print(f"Login successful! Session username: {session.get('username')}")
            print(f"Redirecting to display_home")
            return redirect(url_for("display_home"))
        else:
            msg = "Incorrect username or password. Try again."
            form.username.data = ""
            form.password.data = ""
    
    print(f"Rendering login page, session: {session.get('username')}")
    return render_template("login.html", title="Login Page", content="Enter your username and password.", form=form, msg=msg)

# Logout Routing
@app.route('/logout')
def logout():
    session.pop("username", None)
    return redirect(url_for('display_login'))

# Search Page
@app.route('/search', methods=['GET', 'POST'])
def search_page():
    if CS.notLoggedIn():
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
            records=records,
            CS=CS
        )

    return render_template(
        'search.html',
        sform=sform,
        title="Search Tasks",
        content="Search through active tasks and users.",
        CS=CS
    )

# Admin Actions Page - ( Only Visible To Admin )
@app.route('/admin-actions', methods=['GET', 'POST'])
def admin_actions():
    if CS.notLoggedIn() or CS.getUsername() != "admin":
        return redirect(url_for("display_login"))
    
    task_form = AddTaskForm()
    user_form = AddUserForm()
    
    # Handle Add Task form submission
    if task_form.validate_on_submit() and 'task_submit' in request.form:
        title = task_form.title.data
        body = task_form.body.data
        role = task_form.role.data
        assigned_user = Users.query.filter_by(role=role).first()
        task = Tasks(
            title=title,
            body=body,
            assigned_to=assigned_user.id if assigned_user else None,
            created_by=Users.query.filter_by(username=CS.getUsername()).first().id,
            date_created=datetime.utcnow().strftime("%Y%m%d"),
            completed=0
        )
        db.session.add(task)
        db.session.commit()
        return redirect(url_for("admin_actions"))
    
    # Handle Add User form submission
    if user_form.validate_on_submit() and 'user_submit' in request.form:
        username = user_form.username.data
        password = user_form.password.data
        role = user_form.role.data
        new_user = Users(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("admin_actions"))
    
    return render_template(
        "admin-actions.html",
        title="Admin Operations",
        content="Use forms to complete the following actions:",
        task_form=task_form,  # For add-task.html
        user_form=user_form,  # For add-user.html
        CS=CS
    )


# Add Task Page - ( Extends Admin Actions )
@app.route('/add-task', methods=['GET', 'POST'])
def display_add_task():
    if CS.notLoggedIn():
        return redirect(url_for("display_login"))

    return render_template("add-task.html", title="Add Task", content="Content!")

# Add User Page - ( Extends Admin Actions)
app.route('/add-user', methods=['GET','POST'])
def display_add_user():
    if CS.notLoggedIn():
        return redirect(url_for("display_login"))
    
    return render_template("add-user.html", title="Add User", content="Content!")

# EMPLOYEES PAGE
@app.route('/employees', methods=['GET'])
def display_employees():
    if CS.notLoggedIn():
        return redirect(url_for("display_login"))

    employees = Users.query.all()
    employee_columns = [column.name for column in Users.__table__.columns]

    return render_template(
        "employees.html",
        title="Employee Info Page!",
        content="View all employee information on this page.",
        employees=employees,
        employee_columns=employee_columns,
        CS=CS
    )

# ALL TASKS PAGE
@app.route('/all-tasks', methods=['GET', 'POST'])
def display_tasks():
    if CS.notLoggedIn():
        return redirect(url_for("display_login"))

    tasks = Tasks.query.all()
    task_columns = [column.name for column in Tasks.__table__.columns]

    return render_template(
        "all-tasks.html",
        title="All Tasks Page!",
        content="View all active tasks on this page.",
        form=form,
        tasks=tasks,
        task_columns=task_columns,
        CS=CS
    )
