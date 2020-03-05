from flask import Blueprint, render_template, request, flash, redirect, url_for
from ..models import User, Images
from ..ml_model import prediction
from app import basedir
import time
import scipy.misc
from .. import db
from PIL import Image
import urllib.request

main = Blueprint('main', __name__, template_folder='templates')


@main.route('/')
def home():
    return render_template("home.html")


@main.route('/chat_room', methods=["POST", "GET"])
def chat_room():
    user_list = db.session.query(User.name).all()
    user_list =([x[0] for x in user_list])
    return render_template("chat_room.html", userlist=user_list)


@main.route('/register', methods=["POST"])
def register():
    nickname = request.form['name']
    email = request.form['email']
    try:
        get_user = User.query.filter_by(name=nickname).first()
        user_name = get_user.name
        user_email = get_user.email
        if nickname == user_name or email == user_email:
            flash("This email or nick name is already use in chat")
        else:
            user = User(name=nickname,
                        email=email)
            db.session.add(user)
            db.session.commit()
            flash("Registered successfully")
    except AttributeError:
        user = User(name=nickname,
                    email=email)
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully")
    return redirect(url_for('main.chat_room'))


@main.route('/writing')
def writing():

    return render_template("sheet.html")


@main.route('/image', methods=["POST"])
def image():
    data = request.form['img']
    img = Image.open(urllib.request.urlopen(data))
    result = prediction(img)
    predict = result[0][0]
    filtered_image = result[2]
    img_name = time.strftime("%Y%m%d-%H%M%S")
    img_name = "".join([img_name, "_", str(predict), ".jpg"])
    try:
        path_image = "/".join([basedir, "captured_image", img_name])
        filtered_image.save(path_image)
    except FileNotFoundError:
        info = "Files problem"
        return render_template("sheet.html", predict=predict, info=info)

    image_to_db = Images(predict=int(predict), array=data)
    db.session.add(image_to_db)
    db.session.commit()
    print(predict)
    return render_template("sheet.html", predict=predict)
