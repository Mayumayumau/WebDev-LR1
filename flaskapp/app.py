from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm, RecaptchaField
from werkzeug.utils import secure_filename
from wtforms import FileField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_wtf.file import FileRequired, FileAllowed
from flask_bootstrap import Bootstrap
import os

app = Flask(__name__)
bootstrap = Bootstrap(app)
# TODO: make a random key

app.config['SECRET_KEY'] = 'some_key'

# CAPTCHA
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LeJAGYfAAAAAPdtZRMU9-LdJMLjRIbqnfQosMIr'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LeJAGYfAAAAAFmKVIXr6t3nA0oe48Fi5yOMltHb'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}


class CollageForm(FlaskForm):
    img1 = FileField("Upload image 1", validators=[FileRequired(),
                                                   FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    img2 = FileField("Upload image 2", validators=[FileRequired(),
                                                   FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    shape = SelectField("Collage shape", choices=[("Vertical", "Vertical"), ("Horizontal", "Horizontal")],
                        validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField("Submit", validators=[DataRequired()])


@app.route("/", methods=["GET", "POST"])
def index():
    form = CollageForm()
    filename1 = None
    filename2 = None
    if form.validate_on_submit():
        filename1 = os.path.join('static', secure_filename(form.img1.data.filename))
        filename2 = os.path.join('static', secure_filename(form.img2.data.filename))
        form.img1.data.save(filename1)
        form.img2.data.save(filename2)
        return redirect(url_for("result", image1=filename1, image2=filename2))

    return render_template("index.html", template_form=form, image1=filename1, image2=filename2)

@app.route("/result", methods=["GET"])
def result():
    return render_template("result.html", image1=request.args.get('image1'), image2=request.args.get('image2'))
