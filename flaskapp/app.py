from flask import Flask, render_template, request
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import FileField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_wtf.file import FileRequired, FileAllowed

app = Flask(__name__)

# TODO: make a random key

app.config['SECRET_KEY'] = 'some_key'

# TODO: CAPTCHA

class CollageForm(FlaskForm):
    img = FileField("Upload image 1", validators=[FileRequired(),
                                                         FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    shape = SelectField("Collage shape", choices=[("Vertical", "Vertical"), ("Horizontal", "Horizontal")],
                        validators=[DataRequired()])
    submit = SubmitField("Submit", validators=[DataRequired()])

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


