
from flask import Flask, render_template, request, redirect, session
import uuid
import random
import os
import qrcode
import base64
from flask import send_file
from io import BytesIO

from flask import request

import firebase_admin
from firebase_admin import credentials, db as firebase_db
import json
from firebase_admin import credentials

firebase_key = os.environ.get("FIREBASE_KEY")
cred = credentials.Certificate(json.loads(firebase_key))

firebase_admin.initialize_app(cred)


app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "carebridge_secret"


users = {}
# temporary storage (later replace with Firebase)
registered_users = {}
# store all donations (temporary storage)
food_donations = []

accessory_donations = []

# Example storage (you already have something like this)

from flask_sqlalchemy import SQLAlchemy

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///carebridge.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    donor_type = db.Column(db.String(50))
    age = db.Column(db.Integer)
    color = db.Column(db.String(120))   # NEW COLUMN


class FoodDonation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20))
    food_type = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    unit = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    location = db.Column(db.String(200))
    message = db.Column(db.String(300))





class AccessoryDonation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20))
    item_type = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    phone = db.Column(db.String(20))
    location = db.Column(db.String(200))




def get_user_by_card_id(card_id):
    return registered_users.get(card_id)


# ---------- CONTEXT PROCESSOR ----------


import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def generate_qr(data):
    import qrcode
    import base64
    from io import BytesIO

    qr = qrcode.QRCode(
        version=None,        # auto size
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,         # bigger blocks
        border=4             # VERY IMPORTANT for scanning
    )

    qr.add_data(data)
    qr.make(fit=True)

    # Strong contrast (best for scanning)
    img = qr.make_image(fill_color="goldenrod").convert("RGBA")

    # Remove white background manually 
    datas = img.getdata() 
    newData = [] 
    for item in datas: 
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
             newData.append((255, 255, 255, 0)) 
             # transparent 
        else:
             newData.append(item) 
    img.putdata(newData)

    buffer = BytesIO()
    img.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode()


@app.context_processor
def inject_user():
    return dict(logged_in=("user" in session))




# ---------- BASIC PAGES ----------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")



@app.route("/map_view")
def map_view():
    return render_template("map_view.html")


@app.route("/auth")
def auth():
    return render_template("auth.html")


@app.route("/send_message", methods=["POST"])
def send_message():

    name = request.form["name"]
    email = request.form["email"]
    message = request.form["message"]

    print("New message from:", name)
    print("Email:", email)
    print("Message:", message)

    return "Message Sent Successfully"

from flask import session, redirect, url_for

@app.route("/donate_food", methods=["GET", "POST"])
def donate_food():

    # 🔒 force login
    if "user" not in session:
        return redirect("/auth")

    if request.method == "POST":

        user = session["user"]

        quantity = request.form.get("quantity")
        unit = request.form.get("unit")
        custom_unit = request.form.get("custom_unit")

        if unit == "other" and custom_unit:
            unit = custom_unit

        donation = FoodDonation(
            user_id=user["id"],
            food_type=request.form.get("food_type"),
            quantity=request.form.get("quantity"),
            unit=unit,
            phone=request.form.get("phone"),
            location=request.form.get("location"),
            message=request.form.get("message")
        )

        db.session.add(donation)
        db.session.commit()

        # SEND TO FIREBASE
        ref = firebase_db.reference("donations")

        ref.push({
            "user_id": user["id"],
            "food_type": request.form.get("food_type"),
            "quantity": request.form.get("quantity"),
            "phone": request.form.get("phone"),
            "location": request.form.get("location"),
            "message": request.form.get("message")
        })
        firebase_db.reference("alerts").set({
            "status": False
        })
        food_donations.append(donation)

        return redirect("/donation_success")

    return render_template("donate_food.html")








@app.route("/donate_accessories", methods=["GET","POST"])
def donate_accessories():

    if "user" not in session:
        return redirect("/auth")

    if request.method == "POST":

        user = session["user"]

        donation = AccessoryDonation(
            user_id=user["id"],
            item_type=request.form.get("item_type"),
            quantity=request.form.get("quantity"),
            phone=request.form.get("phone"),
            location=request.form.get("location")
        )

        db.session.add(donation)
        db.session.commit()

        accessory_donations.append(donation)

        # SEND ACCESSORY DATA TO FIREBASE
        ref = firebase_db.reference("accessory_donations")

        ref.push({
            "user_id": user["id"],
            "item_type": request.form.get("item_type"),
            "quantity": request.form.get("quantity"),
            "phone": request.form.get("phone"),
            "location": request.form.get("location")
        })

        return redirect("/donation_success")

    return render_template("donate_accessories.html")



@app.route("/donor/<user_id>")
def donor_profile(user_id):
    user = registered_users.get(user_id)

    if not user:
        return "User not found"

    user_donations = [d for d in food_donations if d["user_id"] == user_id]

    return render_template("donor_profile.html", user=user, donations=user_donations)


@app.route("/donation_success")
def donation_success():
    return render_template("donation_success.html")    






# ---------- SIGNUP ----------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        import uuid, random, re

        age = int(request.form["age"])
        if age <= 0 or age > 120:
            return "Invalid age"

        first = request.form["first_name"]
        last = request.form["last_name"]

        if not re.match(r"^[A-Za-z ]+$", first) or not re.match(r"^[A-Za-z ]+$", last):
            return "Name must contain only letters"

        # ---------- UNIQUE CARD COLOR ----------
        # RANDOM COLOR
        def generate_unique_color():
            r = random.randint(30,220)
            g = random.randint(30,220)
            b = random.randint(30,220)
            return f"linear-gradient(135deg, rgb({r},{g},{b}), rgb({b},{r},{g}))"

        card_color = generate_unique_color()

        # ---------- CARD ID ----------
        card_id = "CB-" + str(uuid.uuid4())[:8].upper()

        existing_user = User.query.filter_by(email=request.form["email"]).first()

        if existing_user:
            return "Email already registered. Please login."

        # ---------- USER OBJECT ----------
        user = {
            "id": card_id,
            "name": first + " " + last,
            "email": request.form["email"],
            "type": request.form["donor_type"],
            "color": generate_unique_color(),
            "user_age": age
        }

        # ---------- QR CODE ----------
        verify_url = request.host_url + "verify/" + card_id
        user["qr"] = generate_qr(verify_url)

        # ---------- STORE IN MEMORY (OLD SYSTEM) ----------
        registered_users[card_id] = user

        # ---------- STORE IN DATABASE (PERMANENT) ----------
        new_user = User(
            id=card_id,
            name=user["name"],
            email=user["email"],
            donor_type=user["type"],
            age=user["user_age"],
            color=card_color
        )

        db.session.add(new_user)
        db.session.commit()

        # ---------- LOGIN SESSION ----------
        session["user"] = {
            "id": card_id,
            "name": user["name"],
            "email": user["email"],
            "type": user["type"],
            "user_age": user["user_age"],
            "color": card_color,
            "qr": user["qr"]
        }

        return redirect("/card")

    return render_template("signup.html")





@app.route("/verify/<card_id>")
def verify(card_id):

    user = User.query.filter_by(id=card_id).first()

    if not user:
        return "Invalid Card"

    verify_url = request.host_url + "verify/" + user.id
    qr_code = generate_qr(verify_url)

    verified_user = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "type": user.donor_type,
        "user_age": user.age,
        "color": user.color,   # IMPORTANT → use stored color
        "qr": qr_code
    }

    return render_template("verify.html", user=verified_user)


@app.route("/card")
def card():
    user = session.get("user")
    if not user:
        return redirect("/signup")
    return render_template("card.html", user=user)

# ---------- PROFILE ----------
@app.route("/profile")
def profile():

    if "user" not in session:
        return redirect("/login")

    user_id = session["user"]["id"]

    food_count = FoodDonation.query.filter_by(user_id=user_id).count()
    acc_count = AccessoryDonation.query.filter_by(user_id=user_id).count()

    return render_template(
        "profile.html",
        user=session["user"],
        food_count=food_count,
        acc_count=acc_count
    )

   


@app.route("/upload_photo", methods=["POST"])
def upload_photo():
    if "user" not in session:
        return redirect("/login")

    photo = request.files.get("photo")

    if photo and photo.filename != "":
        from werkzeug.utils import secure_filename

        filename = secure_filename(photo.filename)

        folder = os.path.join("static", "uploads")
        os.makedirs(folder, exist_ok=True)

        path = os.path.join(folder, filename)
        photo.save(path)

        # IMPORTANT → update session correctly
        user = session["user"]
        user["photo"] = filename
        session["user"] = user   # 🔥 forces session refresh

    return redirect(request.referrer)


@app.route("/remove_photo", methods=["POST"])
def remove_photo():
    if "user" not in session:
        return redirect("/login")

    user = session["user"]

    if "photo" in user:
        filename = user["photo"]
        path = os.path.join("static", "uploads", filename)

        if os.path.exists(path):
            os.remove(path)

        user.pop("photo", None)
        session["user"] = user

    return redirect(request.referrer)    



from flask import session, redirect, url_for
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        user = User.query.filter_by(email=email).first()

        if user:

            verify_url = request.host_url + "verify/" + user.id
            qr_code = generate_qr(verify_url)

            session["user"] = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "type": user.donor_type,
                "user_age": user.age,
                "color": user.color,   # SAME COLOR FROM DATABASE
                "qr": qr_code
            }

            return redirect("/profile")

        else:
            return "Email not registered"

    return render_template("login.html")



@app.route("/send_query", methods=["POST"])
def send_query():

    name = request.form["name"]
    phone = request.form["phone"]
    email = request.form["email"]
    message = request.form["message"]

    ref = db.reference("queries")

    ref.push({
        "name": name,
        "phone": phone,
        "email": email,
        "message": message
    })

    return redirect("/contact")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# ---------- RUN ----------

@app.route("/get_alert")
def get_alert():

    data = firebase_db.reference("alerts").get()

    if not data:
        return {"status": False}

    return data

# ---------- RUN SERVER ----------
import os

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
# test update    