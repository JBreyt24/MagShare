from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.user_model import User # import entire file, rather than class, to avoid circular imports
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
    print(pw_hash)  
    data ={
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
    return render_template('dashboard.html', all_magazines = all_magazines)


@app.route('/login', methods = ['POST'])
def login():
    data = {
        'email' : request.form['email']
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
    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')



# Update Users Controller

@app.route('/account', methods=['POST'])
def update_info():
    if not User.validate_user(request.form):
        return redirect('/') 
    data ={
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "email": request.form['email'],
    }
    id = User.save(data)
    session['user_id'] = id
    session['first_name'] = request.form['first_name']
    return redirect('/user/account')


@app.route('/update/account', methods = ['POST'])
def update_user_info():
    User.update_user(request.form)
    return redirect('/user/account')


# Delete Users Controller
