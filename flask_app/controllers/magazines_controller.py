from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.user_model import User 
from flask_app.models.magazine_model import Magazine 
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
from flask_app.models.subscription_model import Subscription


# Create Magazine

@app.route('/magazine/new')
def magazine():
    if 'user_id' not in session:
        return redirect('/logout')
    return render_template('add_magazine.html')

@app.route('/create/magazine', methods=['POST'])
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
    return render_template("show_magazine.html", magazine=magazine, user=user)

@app.route('/user/account')
def account_magazines():
    if 'user_id' not in session:
        return redirect('/logout')
    magazine_by_user = Magazine.get_all_magazines_w_user()
    return render_template('account.html', magazine_by_user=magazine_by_user)

# Edit Magazine

@app.route('/magazine/edit/<int:id>')
def edit_magazine(id):
    if 'user_id' not in session:
        return redirect('/logout')
    magazine = Magazine.get_one(id)
    return render_template('edit_magazine.html', magazine=magazine)

@app.route('/magazine/update', methods=['POST'])
def update_magazine():
    if not Magazine.validate_magazine_at_edit(request.form):
        return redirect(f"/magazine/edit/{request.form['id']}")

    data = {
        "id": request.form['id'],
        "title": request.form['title'],
        "description": request.form['description']
    }
    Magazine.edit_magazine(data)
    flash("Magazine updated successfully!", "success")
    return redirect('/dashboard')

# Delete Magazine

@app.route('/magazine/destroy/<int:magazine_id>')
def destroy_magazine(magazine_id):
    if 'user_id' not in session:
        return redirect('/logout')
    Magazine.destroy_magazine(magazine_id)
    flash("Magazine deleted successfully!", "success")
    return redirect('/user/account')

# Subscribe Magazine

@app.route('/subscribe/<int:magazine_id>')
def subscribe_to_magazine(magazine_id):
    if 'user_id' not in session:
        return redirect('/logout')

    magazine = Magazine.get_one(magazine_id)

    # Prevent subscribing to own magazine
    if magazine.user_id == session['user_id']:
        flash("You can't subscribe to your own magazine!", "danger")
        return redirect('/dashboard')

    data = {
        "user_id": session['user_id'],
        "magazine_id": magazine_id
    }

    if Subscription.has_user_subscribed(data):
        flash("You've already subscribed to this magazine!", "info")
        return redirect('/dashboard')

    Subscription.subscribe(data)
    flash("Subscribed successfully!", "success")
    return redirect('/dashboard')



@app.route('/unsubscribe/<int:magazine_id>')
def unsubscribe_from_magazine(magazine_id):
    if 'user_id' not in session:
        return redirect('/logout')

    data = {
        "user_id": session['user_id'],
        "magazine_id": magazine_id
    }

    Subscription.unsubscribe(data)
    flash("Unsubscribed successfully!", "success")
    return redirect('/dashboard')
