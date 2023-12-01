from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.user_model import User 
from flask_app.models.magazine_model import Magazine 
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

# Create Magazine

@app.route('/magazine/new')
def magazine():
    if 'user_id' not in session:
        return redirect('/logout')
    return render_template('add_magazine.html')

@app.route('/create/magazine', methods = ['POST'])
def create_magazine():
    if not Magazine.validate_magazine_at_create(request.form):
        return redirect('/magazine/new')
    if "user_id" in session:
        magazine_dict = {
            "user_id": session["user_id"],
            "title": request.form['title'],
            "description": request.form['description'],
    }
    Magazine.save(magazine_dict)
    return redirect('/dashboard')

# Read Magazine

@app.route("/view/magazine/<int:magazine_id>/<int:user_id>")
def view_magazine(magazine_id, user_id):
    if 'user_id' not in session:
        return redirect('/logout')
    magazine = Magazine.get_one(magazine_id)
    user = User.get_one(user_id)
    return render_template("show_magazine.html", magazine = magazine, user = user )


@app.route('/user/account')
def account_magazines():
    if 'user_id' not in session:
        return redirect('/logout')
    magazine_by_user = Magazine.get_all_magazines_w_user()
    return render_template('account.html', magazine_by_user = magazine_by_user)


# Update Magazine



# Delete Magazine

@app.route('/magazine/destroy/<int:magazine_id>')
def destroy_magazine(magazine_id):
    if 'user_id' not in session:
        return redirect('/logout')
    Magazine.destroy_magazine(magazine_id)
    return redirect('/user/account')