from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.user_model import User
from flask import flash

class Subscription:
    myDB = "Exam_erd"

    def __init__(self, data):
        self.id = data['id']
        self.user_id = data['user_id']
        self.magazine_id = data['magazine_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.subscriber = None  # Optional: for relationship purposes

    # Subscribe a user to a magazine
    @classmethod
    def subscribe(cls, data):
        query = """
        INSERT INTO subscribers (user_id, magazine_id)
        VALUES (%(user_id)s, %(magazine_id)s);
        """
        return connectToMySQL(cls.myDB).query_db(query, data)

    # Get all users who subscribed to a specific magazine
    @classmethod
    def get_subscribers_for_magazine(cls, magazine_id):
        query = """
        SELECT users.* FROM subscribers
        JOIN users ON subscribers.user_id = users.id
        WHERE subscribers.magazine_id = %(magazine_id)s;
        """
        results = connectToMySQL(cls.myDB).query_db(query, {'magazine_id': magazine_id})
        subscribers = []
        for row in results:
            subscribers.append(User(row))
        return subscribers

    # Prevent duplicate subscriptions
    @classmethod
    def has_user_subscribed(cls, data):
        query = """
        SELECT * FROM subscribers
        WHERE user_id = %(user_id)s AND magazine_id = %(magazine_id)s;
        """
        results = connectToMySQL(cls.myDB).query_db(query, data)
        return len(results) > 0


    @classmethod
    def get_user_subscriptions(cls, user_id):
        query = """
        SELECT magazines.* FROM subscribers
        JOIN magazines ON magazines.id = subscribers.magazine_id
        WHERE subscribers.user_id = %(user_id)s;
        """
        data = {'user_id': user_id}
        results = connectToMySQL(cls.myDB).query_db(query, data)
        return results if results else []



    
    @classmethod
    def get_magazines_by_user_id(cls, user_id):
        query = """
        SELECT magazines.* FROM subscribers
        JOIN magazines ON subscribers.magazine_id = magazines.id
        WHERE subscribers.user_id = %(user_id)s;
        """
        data = { "user_id": user_id }
        results = connectToMySQL(cls.myDB).query_db(query, data)
        return results


    @classmethod
    def unsubscribe(cls, data):
        query = """
        DELETE FROM subscribers
        WHERE user_id = %(user_id)s AND magazine_id = %(magazine_id)s;
        """
        return connectToMySQL(cls.myDB).query_db(query, data)


