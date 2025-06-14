from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.user_model import User
from flask_app.models.magazine_model import Magazine
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)


@app.route('/')
def index():
    return render_template('login_reg.html')


# Create Users Controller

@app.route('/register', methods=['POST'])
def register():
    if not User.validate_user(request.form):
        return redirect('/')
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    data = {
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "email": request.form['email'],
        "password": pw_hash
    }
    id = User.save(data)
    session['user_id'] = id
    session['first_name'] = request.form['first_name']
    return redirect('/dashboard')


# Read Users Controller

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/logout')
    all_magazines = Magazine.get_all_magazines_w_user()
    return render_template('dashboard.html', all_magazines=all_magazines)


@app.route('/login', methods=['POST'])
def login():
    data = {
        'email': request.form['email']
    }
    user_in_db = User.find_user_login(data)
    if not user_in_db:
        flash("User not registered. Please register to login", "login")
        return redirect('/')
    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        flash("Invalid Email/Password", "login")
        return redirect('/')
    session['user_id'] = user_in_db.id
    session['first_name'] = user_in_db.first_name
    session['last_name'] = user_in_db.last_name
    session['email'] = user_in_db.email
    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# Update Users Controller

@app.route('/update/account', methods=['POST'])
def update_user_info():
    if 'user_id' not in session:
        return redirect('/logout')

    form_data = {
        "id": session['user_id'],
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "email": request.form['email']
    }

    if not User.validate_user_at_edit(form_data):
        return redirect('/user/account')

    User.update_user(form_data)

    # Update session to reflect new info
    session['first_name'] = form_data['first_name']
    session['last_name'] = form_data['last_name']
    session['email'] = form_data['email']

    flash("Your account info has been updated!", "success")
    return redirect('/user/account')
