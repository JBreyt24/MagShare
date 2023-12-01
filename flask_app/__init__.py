from flask import Flask
app = Flask(__name__)
app.secret_key = "Cmin7add9#11" 

# The secret key is needed to run session
# This is one thing that would usually be kept in your git ignore, along with API keys