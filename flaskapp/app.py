from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, BooleanField

app = Flask(__name__)
# TO DO: make a random key
app.config['SECRET_KEY'] = 'some_key'

@app.route("/", methods=["GET", "POST"])
def index():
    return "Hello World"


