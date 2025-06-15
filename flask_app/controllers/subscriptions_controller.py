from flask_app import app
from flask import render_template, redirect, session
from flask_app.models.subscription_model import Subscription
from flask_app.models.magazine_model import Magazine

@app.route('/subscriptions')
def subscriptions_page():
    if 'user_id' not in session:
        return redirect('/logout')
    user_id = session['user_id']
    user_subscriptions = Subscription.get_magazines_by_user_id(user_id)
    return render_template('subscriptions.html', subscriptions=user_subscriptions)
