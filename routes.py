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
                content = "Welcome Admin! You have global super user privileges. All actions are allowed."
            case "employee":
                content = f"Hello {username} your role is {role}, you can check your assigned tasks, and see all tasks!"
            case "manager":
                content = f"Hello {username} your role is {role}, you can see all assigned tasks, and assign tasks to employees!"
        return render_template("index.html", title=f"Welcome {username}!", content=content, CS=CS)
    return redirect(url_for("display_login"))
    

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def display_login():
    if CS.isLoggedIn():
        return redirect(url_for('display_home'))
    
    form = LoginForm()
    msg = ""
    
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        if CS.authenticate(username, password):
            session["username"] = username
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

# My Tasks Page
@app.route('/my-tasks')
def display_my_tasks():
    if CS.notLoggedIn():
        return redirect(url_for("display_login"))
    
    # Fetch all tasks of logged in user
    user_id = Users.query.filter_by(username=CS.getUsername()).first().id

    tasks = Tasks.query.filter_by(assigned_to=user_id, completed=0).all()

    # Query usernames for display
    task_list = map_tasks_to_usernames(tasks)
    
    return render_template(
        'my-tasks.html',
        title="My Tasks",
        content=f"This page shows all tasks assigned to {CS.getUsername()}.",
        tasks=task_list,
        CS=CS
    )

# MY COMPLETED TASKS
@app.route('/my-completed-tasks')
def display_my_completed_tasks():
    if CS.notLoggedIn():
        return redirect(url_for("display_login"))
    
    # Fetch user ID for task query
    user_id = Users.query.filter_by(username=CS.getUsername()).first().id

    # Fetch all completed tasks assigned to the user
    tasks = Tasks.query.filter_by(assigned_to=user_id, completed=1).all()
    
    # Query usernames for display
    task_list = map_tasks_to_usernames(tasks)
    
    return render_template(
        "my-completed-tasks.html",
        title="Completed Tasks Page!",
        content="These are all the tasks marked as complete in the database.",  # Fixed typo: "Theses" to "These"
        tasks=task_list,  # Pass the modified task list
        CS=CS
    )


@app.route('/search', methods=['GET', 'POST'])
def search_page():
    if CS.notLoggedIn():
        return redirect(url_for("display_login"))

    sform = form.SearchForm()

    # Get column names for display in results
    task_columns = [column.name for column in Tasks.__table__.columns]
    user_columns = [column.name for column in Users.__table__.columns]
    
    records = []
    user = None
    searchType = None
    active_task_list = None
    completed_task_list = None

    if request.method == 'POST' and sform.validate_on_submit():
        value = sform.value.data

        if 'search_title' in request.form:
            searchType = "title"
            active_tasks = Tasks.query.filter(Tasks.title.ilike(f"%{value}%"), Tasks.completed == 0).all()
            completed_tasks = Tasks.query.filter(Tasks.title.ilike(f"%{value}%"), Tasks.completed == 1).all()
        elif 'search_description' in request.form:
            searchType = "description"
            active_tasks = Tasks.query.filter(Tasks.body.ilike(f"%{value}%"), Tasks.completed == 0).all()
            completed_tasks = Tasks.query.filter(Tasks.body.ilike(f"%{value}%"), Tasks.completed == 1).all()
        elif 'search_username' in request.form:
            searchType = "username"
            user = Users.query.filter(Users.username.ilike(f"%{value}%")).first()
            if user:
                user_id = user.id
                active_tasks = Tasks.query.filter(Tasks.assigned_to == user_id, Tasks.completed == 0).all()
                completed_tasks = Tasks.query.filter(Tasks.assigned_to == user_id, Tasks.completed == 1).all()
            else:
                active_tasks = []
                completed_tasks = []

        # Map tasks to usernames only if tasks exist
        if active_tasks and completed_tasks:    
            active_task_list = map_tasks_to_usernames(active_tasks)  # Fixed: Use active_tasks
            completed_task_list = map_tasks_to_usernames(completed_tasks)  # Fixed: Use completed_tasks
        elif active_tasks:
            active_task_list = map_tasks_to_usernames(active_tasks)  # Fixed: Use active_tasks
        elif completed_tasks:
            completed_task_list = map_tasks_to_usernames(completed_tasks)  # Fixed: Use completed_tasks

        return render_template(
            'search_result.html',
            title="Search result",
            task_columns=task_columns,
            user_columns=user_columns,
            active_tasks=active_task_list,
            completed_tasks=completed_task_list,
            user=user,
            searchType=searchType,
            searchTerm=value,
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
    if CS.notLoggedIn():
        return redirect(url_for("display_login"))
    
    task_form = AddTaskForm()
    user_form = AddUserForm()
    task_submitted = False
    user_submitted = False
    
    # Handle Add Task form submission
    if task_form.validate_on_submit() and 'task_submit' in request.form:
        title = task_form.title.data
        body = task_form.body.data
        

        user_id = int(task_form.user.data)
        exists = Users.query.filter_by(id=user_id).first().id
        created_by = ""
        if CS.getUsername() == "admin":
            created_by = CS.getID()
        else:
            created_by = CS.getUsername()
            created_by = Users.query.filter_by(username=created_by).first().id

        # Get user ID from table and set 'created_by' variable to number instead of username

        if (exists):

            task = Tasks(
                title=title,
                body=body,
                assigned_to=user_id,
                created_by=created_by,
                date_created=datetime.utcnow().strftime("%m-%d-%y"),
                completed=0
            )
        
            db.session.add(task)
            db.session.commit()
            # Hide form variable
            task_submitted = True
        
    
    # Handle Add User form submission
    if user_form.validate_on_submit() and 'user_submit' in request.form:
        username = user_form.username.data
        password = user_form.password.data
        role = user_form.role.data
        new_user = Users(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        # Hide form variable
        user_submitted = True
        
    
    return render_template(
        "admin-actions.html",
        title="Add Tasks & Users",
        content="Use forms to complete the following actions:",
        task_form=task_form,  # For add-task.html
        user_form=user_form,  # For add-user.html
        task_submitted=task_submitted,
        user_submitted=user_submitted,
        CS=CS
    )


# Add Task Page - ( Extends Admin Actions )
@app.route('/add-task', methods=['GET', 'POST'])
def display_add_task():
    if CS.notLoggedIn():
        return redirect(url_for("display_login"))
    

    return render_template(
        "add-task.html",
        title="Add Task",
        )

# Add User Page - ( Extends Admin Actions)
app.route('/add-user', methods=['GET','POST'])
def display_add_user():
    if CS.notLoggedIn():
        return redirect(url_for("display_login"))
    
    return render_template(
        "add-user.html",
        title="Add User"
        )

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

    # Handle form submissions
    if request.method == 'POST':
        task_id = request.form.get("task_id")
        action = request.form.get("action")
        task = Tasks.query.get(task_id)
        
        if task:
            if action == "mark_complete":
                if CS.getRole() in ["admin", "Manager"]:
                    task.completed = 1
                    db.session.commit()
                    flash("Task marked as complete!", "success")
                else:
                    flash("You do not have permission to mark tasks as complete.", "error")
            elif action == "edit":
                if CS.getRole() in ["admin", "Manager"]:
                    return redirect(url_for('display_edit_task', task_id=task_id))
                else:
                    flash("You do not have permission to edit tasks.", "error")
            elif action == "delete":
                if CS.getRole() in ["admin", "Manager"]:
                    db.session.delete(task)
                    db.session.commit()
                    flash("Task deleted successfully!", "success")
                else:
                    flash("You do not have permission to delete tasks.", "error")
        
        return redirect(url_for('display_tasks'))
    
    # Fetch all incomplete tasks
    tasks = Tasks.query.filter_by(completed=0).all()
    
    # Query usernames for display
    task_list = map_tasks_to_usernames(tasks)
    
    return render_template(
        "all-tasks.html",
        title="All Tasks Page!",
        content="View all active tasks on this page.",
        tasks=task_list,
        CS=CS
    )

# EDIT TASK PAGE
@app.route('/edit-task/<int:task_id>', methods=['GET', 'POST'])
def display_edit_task(task_id):
    if CS.notLoggedIn():
        return redirect(url_for("display_login"))
    
    if CS.getRole() not in ["admin", "Manager"]:
        flash("You do not have permission to edit tasks.", "error")
        return redirect(url_for("display_tasks"))
    
    # Fetch the task to edit
    task = Tasks.query.get_or_404(task_id)
    
    if request.method == 'POST':
        # Update the task with form data
        task.title = request.form.get("title")
        task.body = request.form.get("body")
        task.assigned_to = int(request.form.get("user"))
        db.session.commit()
        flash("Task updated successfully!", "success")
        return redirect(url_for("display_tasks"))
    
    # Prepare task data for display
    creator_username = "Admin" if task.created_by == 999 else "None"
    if task.created_by and task.created_by != 999:
        creator = Users.query.get(task.created_by)
        creator_username = creator.username if creator else "Unknown"
    
    assignee_username = "None"
    if task.assigned_to:
        assignee = Users.query.get(task.assigned_to)
        assignee_username = assignee.username if assignee else "Unknown"
    
    task_data = {
        "id": task.id,
        "title": task.title,
        "body": task.body,
        "assigned_to": task.assigned_to,
        "created_by": creator_username,
        "date_created": task.date_created,
        "assignee_username": assignee_username
    }
    
    # Fetch all users for the dropdown
    users = Users.query.all()
    
    return render_template(
        "edit-task.html",
        title="Edit Task",
        task=task_data,
        users=users,
        CS=CS
    )

# COMPLETED TASKS
@app.route('/completed-tasks')
def display_completed_tasks():
    if CS.notLoggedIn():
        return redirect(url_for("display_login"))
    
    # Fetch all completed tasks
    tasks = Tasks.query.filter_by(completed=1).all()
    
    # Query usernames for display
    task_list = map_tasks_to_usernames(tasks)
    
    return render_template(
        "completed-tasks.html",
        title="Completed Tasks Page!",
        content="These are all the tasks marked as complete in the database.",  # Fixed typo: "Theses" to "These"
        tasks=task_list,  # Pass the modified task list
        CS=CS
    )

### Utility Functions

# Convert assigned_to & created_by id numbers from Tasks table to the corresponding usernames
def map_tasks_to_usernames(tasks):
    """
    Convert a list of Tasks objects into a list of dictionaries with usernames for created_by and assigned_to.
    Args:
        tasks: List of Tasks objects from the database.
    Returns:
        List of dictionaries with task details and usernames.
    """
    task_list = []
    for task in tasks:
        # Get creator username
        creator_username = "Admin" if task.created_by == 999 else "None"
        if task.created_by and task.created_by != 999:
            creator = Users.query.get(task.created_by)
            creator_username = creator.username if creator else "Unknown"
        
        # Get assignee username
        assignee_username = "None"
        if task.assigned_to:
            assignee = Users.query.get(task.assigned_to)
            assignee_username = assignee.username if assignee else "Unknown"
        
        # Add task with usernames to the list
        task_list.append({
            "id": task.id,
            "title": task.title,
            "body": task.body,
            "assigned_to": assignee_username,
            "created_by": creator_username,
            "date_created": task.date_created
        })
    return task_list