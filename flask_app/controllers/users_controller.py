from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.user_model import User
from flask_app.models.magazine_model import Magazine
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
from flask_app.models.subscription_model import Subscription


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
    
    user_id = session['user_id']
    all_magazines = Magazine.get_all_magazines_w_user()
    user_subscriptions = Subscription.get_user_subscriptions(user_id)
    subscribed_ids = {mag['id'] for mag in user_subscriptions}  # Set of magazine IDs the user is subscribed to

    return render_template('dashboard.html', all_magazines=all_magazines, subscribed_ids=subscribed_ids)



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


# Subscriptions

@app.route('/subscriptions')
def my_subscriptions():
    if 'user_id' not in session:
        return redirect('/logout')
    subscriptions = Subscription.get_user_subscriptions(session['user_id'])  # ✅ FIXED
    return render_template('subscriptions.html', subscriptions=subscriptions)


@app.route('/user/account')
def user_account_magazines():
    if 'user_id' not in session:
        return redirect('/logout')
    
    magazine_by_user = Magazine.get_all_magazines_w_user()
    user_subscriptions = Subscription.get_user_subscriptions(session['user_id'])  # NEW

    return render_template('account.html', magazine_by_user=magazine_by_user, subscriptions=user_subscriptions)


# Password Update

@app.route('/update/password', methods=['POST'])
def update_password():
    if 'user_id' not in session:
        return redirect('/logout')

    data = {
        'id': session['user_id'],
        'current_password': request.form['current_password'],
        'new_password': request.form['new_password'],
        'confirm_password': request.form['confirm_password']
    }

    user = User.get_by_id({'id': session['user_id']})

    if not bcrypt.check_password_hash(user.password, data['current_password']):
        flash("Current password is incorrect", "danger")
        return redirect('/user/account')

    if len(data['new_password']) < 8:
        flash("New password must be at least 8 characters", "danger")
        return redirect('/user/account')

    if data['new_password'] != data['confirm_password']:
        flash("New password and confirmation do not match", "danger")
        return redirect('/user/account')

    hashed_pw = bcrypt.generate_password_hash(data['new_password'])
    User.update_password({'id': session['user_id'], 'password': hashed_pw})

    flash("Password successfully updated!", "success")
    return redirect('/user/account')
