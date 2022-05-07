from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm, RecaptchaField
from werkzeug.utils import secure_filename
from wtforms import FileField, SubmitField, SelectField, EmailField, StringField, IntegerRangeField
from wtforms.validators import DataRequired, Email, NumberRange
from flask_wtf.file import FileRequired, FileAllowed
from flask_bootstrap import Bootstrap
import os
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from flask_mail import *

app = Flask(__name__)
app.debug = True
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = os.urandom(12).hex()
app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'fb45d7521fff8f'
app.config['MAIL_PASSWORD'] = '47e5511eb1a6cf'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

# Ключи для капчи
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LeJAGYfAAAAAPdtZRMU9-LdJMLjRIbqnfQosMIr'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LeJAGYfAAAAAFmKVIXr6t3nA0oe48Fi5yOMltHb'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}


class CollageForm(FlaskForm):
    name = StringField("Your name", validators=[DataRequired()])
    email = EmailField("E-mail address", validators=[Email(), DataRequired()])
    img1 = FileField("Upload image 1", validators=[FileRequired(),
                                                   FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    img2 = FileField("Upload image 2", validators=[FileRequired(),
                                                   FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    shape = SelectField("Collage shape", choices=[("Vertical", "Vertical"), ("Horizontal", "Horizontal")],
                        validators=[DataRequired()])
    border_width = IntegerRangeField("Border width", default=0, validators=[NumberRange(min=0, max=50)])
    divider_width = IntegerRangeField("Divider width", validators=[NumberRange(min=0, max=50)])
    # recaptcha = RecaptchaField()
    submit = SubmitField("Submit", validators=[DataRequired()])


# главная страница приложения
@app.route("/", methods=["GET", "POST"])
def index():
    # очищаем папку static от файлов, загруженных в прошлой сессии
    files = os.listdir("./static")
    if len(files) > 1:
        for file_path in files:
            if file_path != 'style.css':
                os.remove('./static/' + file_path)
    #  Создаем форму. В случае успешной валидации, переходим на страницу с результатом
    form = CollageForm()
    filename1 = None
    filename2 = None
    collage_shape = None
    name = None
    if form.validate_on_submit():
        filename1 = os.path.join('./static', secure_filename(form.img1.data.filename))
        filename2 = os.path.join('./static', secure_filename(form.img2.data.filename))
        collage_shape = form.shape.data
        name = form.name.data
        email = form.email.data
        form.img1.data.save(filename1)
        form.img2.data.save(filename2)
        border_width = form.border_width.data
        divider_width = form.divider_width.data

        return redirect(
            url_for("result", image1=filename1, image2=filename2, shape=collage_shape, name=name, email=email,
                    border_width=border_width, divider_width=divider_width))

    return render_template("index.html", form=form)


def combine_pics(img1, img2, shape, border_width, divider_width):
    img_combined = None
    # приводим изображения к одинаковой высоте или ширине в зависимости от формы коллажа
    if shape == 'Vertical':
        if img1.width < img2.width:
            img2.thumbnail((img1.width, img2.height))
        elif img1.width > img2.width:
            img1.thumbnail((img2.width, img1.height))
        # создаем фон для коллажа и копируем на него оба изображения
        width = img1.width + 2 * border_width
        height = img1.height + img2.height + divider_width + border_width * 2
        img_combined = Image.new('RGB', (width, height), (0, 0, 0))
        img_combined.paste(img1, (border_width, border_width))
        img_combined.paste(img2, (border_width, img1.height + border_width + divider_width))
    else:
        if img1.height < img2.height:
            img2.thumbnail((img2.width, img1.height))
        elif img1.height > img2.height:
            img1.thumbnail((img1.width, img2.height))
        img_combined = Image.new('RGB', (img1.width + img2.width, img1.height))
        img_combined.paste(img1, (0, 0))
        img_combined.paste(img2, (img1.width, 0))
    return img_combined


@app.route("/result", methods=["GET"])
def result():
    # получаем назвния файлов и нужную форму коллажа из параметров функции redirect
    image1_path = request.args.get('image1')
    image2_path = request.args.get('image2')
    shape = request.args.get('shape')
    # открываем изображения
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)
    # комбинируем изображения и сохраняем файл
    border_width = int(request.args.get('border_width'))
    divider_width = int(request.args.get('divider_width'))
    collage = combine_pics(image1, image2, shape, border_width, divider_width)
    collage.save('./static/collage.jpg')
    # трансформируем все три изображения в numpy массивы
    np_image1 = np.array(image1)
    np_image2 = np.array(image2)
    np_collage = np.array(collage)
    # транспонируем массивы
    image1_transposed = np_image1.transpose()
    image2_transposed = np_image2.transpose()
    collage_transposed = np_collage.transpose()
    # создаем массивы и записываем в них количество значений для каждой величины R, G  и B
    rgb1 = [[]] * 3
    rgb2 = [[]] * 3
    rgb_collage = [[]] * 3
    for i in range(3):
        rgb1[i], bin1 = np.histogram(image1_transposed[i], bins=256)
        rgb2[i], bin1 = np.histogram(image2_transposed[i], bins=256)
        rgb_collage[i], bin1 = np.histogram(collage_transposed[i], bins=256)
    # создаем графики по получившимся данным и сохраняем их в виде изображений
    fig1 = plt.figure(figsize=(4, 4))
    viewer1 = fig1.add_subplot(1, 1, 1)
    viewer1.plot(rgb1[0], color='r')
    viewer1.plot(rgb1[1], color='g')
    viewer1.plot(rgb1[2], color='b')
    fig1.savefig('./static/hist1.png')
    fig2 = plt.figure(figsize=(4, 4))
    viewer2 = fig2.add_subplot(1, 1, 1)
    viewer2.plot(rgb2[0], color='r')
    viewer2.plot(rgb2[1], color='g')
    viewer2.plot(rgb2[2], color='b')
    fig2.savefig('./static/hist2')
    fig3 = plt.figure(figsize=(4, 4))
    viewer3 = fig3.add_subplot(1, 1, 1)
    viewer3.plot(rgb_collage[0], color='r')
    viewer3.plot(rgb_collage[1], color='g')
    viewer3.plot(rgb_collage[2], color='b')
    fig3.savefig('./static/hist3')

    name = request.args.get("name")
    email = request.args.get("email")
    msg = Message("your collage", sender="maya@mailtrap.io", recipients=[email])
    msg.body = f"Hey {name}, your collage is attached."
    with app.open_resource("./static/collage.jpg") as fp:
        msg.attach("collage.jpg","image/png", fp.read())
        mail.send(msg)
    return render_template("result.html", image1=image1_path, image2=image2_path, collage=collage
                           , name=name, email=email)
