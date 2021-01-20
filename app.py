from flask import Flask, flash, request, redirect, url_for, make_response, session
from flask_login import LoginManager
from flask_hashing import Hashing
from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, IntegerField
from wtforms.validators import DataRequired, EqualTo
import flask  # BSD License (BSD-3-Clause)
import os
import hashlib
from werkzeug.utils import secure_filename
from bdd.database import db, init_database, populate_database, clear_database
from bdd.objects.washingMachine import machineList, initWashingMachineList, findMachineWith404
from bdd.dbMethods import addUser, findUser, updateUser
from datetime import datetime, date


app = Flask(__name__)
hashing = Hashing(app)
app.config.from_object('config')

db.init_app(app)

''' Initialise la base de données et la liste des machines disponibles'''
def initApp ():
    init_database()
    initWashingMachineList ()


with app.app_context():
    initApp ()



# Route de base qui conduit à Login si l'utilisateur n'est pas identifié et à home si il l'est
@app.route('/', methods=["GET", "POST"])
def home():
    if not session.get('logged_in'):
        return flask.render_template('login.html.jinja2')
    else:
        return flask.render_template("home.html.jinja2")

# Page de login
@app.route('/login', methods=['GET', 'POST'])
def do_admin_login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        # Bon id/mdp ?
        result = request.form
        username = result['username']
        if findUser(username) == None :
            flash('wrong username')
            return flask.render_template("login.html.jinja2")
        user = findUser(username)
        hashPassword = user.password
        passw = result['password']   
        if hashing.check_value(hashPassword, passw, salt='abcd'): 
            session['username'] = username
            print(session['username'])
            session['logged_in'] = True
        else:
            flash('wrong password!')
        print(session.get('username'))    
        return redirect(url_for('home'))
    else :
        return flask.render_template("login.html.jinja2")    
    #return home()

# logout
@app.route("/logout")
def logout():
    session['logged_in'] = False
    #return home()
    return redirect(url_for('home'))

# signin
@app.route("/signin", methods=['GET', 'POST'])
def signin():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        #Ajout des données dans la bdd
        result = request.form
        username = result['username']
        password = result['password']
        
        # Pour l'instant en clair mais à améliorer : hashage
        hashPassword = hashing.hash_value(password, salt='abcd')
        if findUser(username) == None :
            addUser(username, hashPassword)
            print(hashPassword)
            session['logged_in'] = True
        else :
            flash('Oups ! Sign in failed, user already exists')
        return redirect(url_for('home'))
    else :
        flash('Username must have between 4 and 25 characters')
    return flask.render_template("signin.html.jinja2")


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired()])
    

class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired()])

class ChangePassword(Form):
    password = PasswordField('New Password', [validators.DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Repeat password')

@app.route('/changePassword', methods=["GET", "POST"])
def change():
    form = ChangePassword(request.form)
    result=request.form
    if request.method == 'POST':
        if form.validate() : 
            result=request.form
            username = session.get('username')
            user = findUser(username)
            password = result['password']
            hashPassword = hashing.hash_value(password, salt='abcd')
            updateUser (user, username, hashPassword)
            return flask.render_template("home.html.jinja2")
        else :
            flash('Issue')    
    return flask.render_template('changePassword.html.jinja2')

@app.route('/profil', methods=["GET"])
def profil():
    return flask.render_template('profil.html.jinja2')    


@app.route('/general', methods=["GET", "POST"])
def general():
    if not session.get('logged_in'):
        return flask.render_template('login.html.jinja2')
    else:
        return flask.render_template("general.html.jinja2")
    

''' Sur ce endpoint, on reset la base de données'''
@app.route('/reset', methods=["GET", "POST"])
def reset():
    clear_database()
    initApp ()
    return flask.render_template("home.html.jinja2")

## Pages pour montrer le fonctionnement de WashingMachine
''' Imprime la liste des machines à laver (ce sont des objet dons pas beaux...)
    Nicolas si besoin tu devrais pouvoir avoir leur nom avec machine.label et leur index avec machine.index'''
@app.route('/machine/findAll', methods=["GET", "POST"])
def findAllMachines():
    print (machineList)
    return flask.render_template("home.html.jinja2")

''' Accède à la machine id et regarde les réservations sur une journée à passer en paramètre (type date)'''
@app.route('/machine/<id>/check', methods=["GET", "POST"])
def check(id):
    machine = findMachineWith404 (id)
    print (machine.checkDate(date.today()))
    return flask.render_template("home.html.jinja2")

''' Accède à la machine id et regarde les réservations de tous les temps '''
@app.route('/machine/<id>/findAll', methods=["GET", "POST"])
def findAllReservations(id):
    machine = findMachineWith404 (id)
    print (machine.findAll())
    return flask.render_template("home.html.jinja2")

''' réserve la machine pour un créneau d'une durée prédéfinie pour une horodate '''
@app.route('/machine/<id>/reserve', methods=["GET", "POST"])
def reserve(id):
    machine = findMachineWith404 (id)
    machine.reserve(datetime.today())
    return flask.render_template("home.html.jinja2")

## Pages pour montrer le fonctionnement de User
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
    app.secret_key = os.urandom(16)
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
