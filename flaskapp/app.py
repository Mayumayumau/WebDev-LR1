from flask import Flask, render_template, request
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

# TODO: CAPTCHA

# photos = UploadSet('photos', IMAGES)

class CollageForm(FlaskForm):
    img1 = FileField("Upload image 1", validators=[FileRequired(),
                                                         FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    img2 = FileField("Upload image 2", validators=[FileRequired(),
                                                         FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    shape = SelectField("Collage shape", choices=[("Vertical", "Vertical"), ("Horizontal", "Horizontal")],
                        validators=[DataRequired()])
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


    return render_template("index.html", template_form=form, image1=filename1, image2=filename2)


