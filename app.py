from flask import Flask, flash, request, redirect, url_for, make_response, session
import flask  # BSD License (BSD-3-Clause)
import os
from werkzeug.utils import secure_filename
from bdd.database import db, init_database, populate_database, clear_database
from bdd.objects.washingMachine import WashingMachine
from bdd.dbMethods import addUser, findUser, updateUser
from datetime import datetime, date


app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)

with app.app_context():
    init_database()
    machine = WashingMachine ("1")


@app.route('/', methods=["GET", "POST"])
def home():
    return flask.render_template("home.html.jinja2")

## Pages pour montrer le fonctionnement de WashingMachine
@app.route('/machine/check', methods=["GET", "POST"])
def check():
    print (machine.checkDate(date.today()))
    return flask.render_template("home.html.jinja2")

@app.route('/machine/findAll', methods=["GET", "POST"])
def findAll():
    print (machine.findAll())
    return flask.render_template("home.html.jinja2")

@app.route('/machine/reserve', methods=["GET", "POST"])
def reserve():
    machine.reserve(datetime.today())
    return flask.render_template("home.html.jinja2")

## TODO: Pages pour montrer le fonctionnement de User
@app.route('/user/create', methods=["GET", "POST"])
def create():
    addUser ("admin", "password")
    return flask.render_template("home.html.jinja2")

@app.route('/user/find', methods=["GET", "POST"])
def find():
    print (findUser("admin"))
    return flask.render_template("home.html.jinja2")

@app.route('/user/update', methods=["GET", "POST"])
def update():
    user = findUser("admin")
    updateUser (user, "admin2", "new password")
    return flask.render_template("home.html.jinja2")



@app.errorhandler(404)
def not_found(e):
    return flask.render_template("404.html.jinja2"), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
