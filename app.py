from flask import Flask, redirect, url_for, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, login_required
import os
import random

basedir=os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite'),
    SECRET_KEY = 'secret_key'
)

db = SQLAlchemy(app)
from models import *

login = LoginManager(app)
login.login_view = "/ins" #Si la conncection n'est pas réussi => page connection

@login.user_loader
def load_user(id):
    return UserModels.query.get(int(id))  #Récupére tous l'id d'utilisateur

def get_objs(model, name_lis):
    entree_objs = []
    for name in name_lis:
        for obj in model.query.filter(model.desc.like("%" + name + "%")):
            if obj in entree_objs:
                continue
            entree_objs.append(obj)
    for obj in model.query.all():
        if obj in entree_objs:
            continue
        entree_objs.append(obj)
    entree_objs = entree_objs[:3]
    return entree_objs

@app.route("/")
@login_required
def index():
    objs = CollectModels.query.filter_by(user_id=current_user.id).all()
    name_lis = []
    for obj in objs:
        name_lis.append(FoodModels.query.filter_by(id=obj.food_id).first().name)

    entree_objs = get_objs(EntreeModels, name_lis)
    plat_objs = get_objs(PlatModels, name_lis)
    dessert_objs = get_objs(DessertModels, name_lis)


    food_lis = FoodModels.query.all()
    food_objs = []
    if food_lis:
        food_objs = random.choices(food_lis, k=4)

    return render_template("index.html",
                           entree_objs=entree_objs,
                           plat_objs=plat_objs,
                           dessert_objs=dessert_objs,
                           food_objs=food_objs,
                           )

@app.route("/ins", methods=["GET", "POST"]) #Connection
def ins():
    FM = request.form.get
    msg = ""
    if request.method == "POST":
        try:
            email = FM("email", "").strip() #Efface les espaces des côtés
            pwd = FM("password", "").strip()
            assert all([email, pwd]), "Le champ est vide !"
            #si la condition est fausse, alors "le champ est vide"
            objs = UserModels.query.filter_by(email=email)
            assert objs.count() != 0, "Utilisateur n'existe pas !"
            #si la condition est fausse, alors "utilisateur n'existe pas"
            assert objs.first().verify_user_password(pwd), "Mot de passe incorrect"

            login_user(objs.first())
            return redirect(url_for("index"))
        except Exception as e:
            print("====> e: ", e)
            msg = e.args[0] if e.args else "Erreur de connection !"
    return render_template("Ins.html",msg=msg)

@app.route("/register", methods=["GET", "POST"]) #Inscription
def register():
    if request.method == "POST":
        try:
            first_name = request.form.get("first_name", "")
            last_name = request.form.get("last_name", "")
            email = request.form.get("email", "")
            password = request.form.get("password", "")
            print(first_name, last_name, email, password)

            objs = UserModels.query.filter_by(email=email)
            assert objs.count() == 0, "Utilisateur existe !"

            user = UserModels(email=email)
            user.set_user_password(password)
            user.first_name = first_name
            user.last_name = last_name

            db.session.add(user)
            db.session.commit()
        except Exception:
            return redirect(url_for("ins"))
    return render_template("Ins.html")

@app.route("/add_collect/<nid>")
def add_collect(nid):
    print("nid: ", nid)
    objs = FoodModels.query.filter_by(id=nid)
    coll_objs = CollectModels.query.filter_by(user_id=current_user.id, food_id=nid)
    print("objs: ", objs.count())
    if coll_objs.count() == 0:
        db.session.add(
            CollectModels(
                user_id=current_user.id,
                food_id=nid,
            )
        )
    else:
        coll_objs.delete()
    db.session.commit()
    return redirect(request.args.get("target", "/shop"))


@app.route("/wishlist")
def wishlist():
    objs = CollectModels.query.filter_by(user_id=current_user.id).all()
    for obj in objs:
        obj.attr = FoodModels.query.filter_by(id=obj.food_id).first()
    return render_template("wishlist.html", objs=objs)

@app.route("/shop")
def shop():
    search = str(request.args.get("search", "")).strip()
    if not search:
        objs = FoodModels.query.filter().limit(8)
    else:
        objs = FoodModels.query.filter(
            FoodModels.name.like("%" + search + "%")
        )
    for obj in objs:
        print(obj)
        if CollectModels.query.filter_by(food_id=obj.id, user_id=current_user.id).count():
            obj.collect = True
        else:
            obj.collect = False
    return render_template("shop.html",objs=objs)

@app.route("/single_product/<nid>") 
def single_product(nid):
    try:
        obj = FoodModels.query.filter_by(id=nid).first()
        if CollectModels.query.filter_by(food_id=obj.id, user_id=current_user.id).count():
            obj.collect = True
        else:
            obj.collect = False
    except Exception:
        return redirect(url_for("shop"))
    return render_template("single-product.html", obj=obj)

@app.route("/add_note", methods=["POST"])
def add_note():
    prenoom = request.form.get("prenoom","")
    email = request.form.get("email","")
    subject = request.form.get("subject","")
    message = request.form.get("message","")

    obj = NoteModels(
        user_id=current_user.id,
        prenoom=prenoom,
        email=email,
        subject=subject,
        message=message,
    )
    db.session.add(obj)
    db.session.commit()
    # return redirect("/")
    return {"ok":"success"}

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)