from flask import Flask, flash, request, redirect, url_for, make_response, session
import flask  # BSD License (BSD-3-Clause)
import os
from werkzeug.utils import secure_filename
from bdd.database import db, init_database, populate_database, clear_database
from bdd.dbMethods import findAllVisitor, findNameUsage, findVisitorById
from api.nameAPI import saveNameInfo
from forms.hello_form import HelloForm
from forms.randomWord_form import NumberWordForm
from src.calcul import randomWords


app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)

with app.app_context():
    init_database()


@app.route('/', methods=["GET", "POST"])
def home():
    username = None
    if 'user' in session:
        user = session['user']
        visitor = findVisitorById(user)
        if visitor: username = visitor.name
    form = HelloForm()
    if form.validate_on_submit():
        name = form.name.data.lower().replace('<', '').replace('>', '').replace(
            '/', '').replace('\\', '').replace('&', '').replace('"', '').replace("'", '')
        id = saveNameInfo(name)
        session['user'] = id
        return flask.redirect(flask.url_for('helloW', name=name))
    else:
        return flask.render_template("home.html.jinja2", form=form, username=username)


@app.route('/hello/<name>')
def helloW(name):
    usages = findNameUsage(name)
    return flask.render_template("hello.html.jinja2", name=name, usages=usages)


@app.route('/about')
def about():
    return flask.render_template("about.html.jinja2")


@app.route('/word', methods=["GET", "POST"])
def word():
    form = NumberWordForm()
    if form.validate_on_submit():
        words = randomWords(form.number.data)
        return flask.render_template("word.html.jinja2", form=form, words=words)
    return flask.render_template("word.html.jinja2", form=form)


@app.route('/visitors')
def visitors_list():
    user = None
    if 'user' in session:
        user = session['user']
    return flask.render_template("visitors_list.html.jinja2", visitors=findAllVisitor(), user=user)


@app.route('/reset')
def reset():
    clear_database()
    init_database()
    if 'user' in session : session.pop('user')
    return flask.redirect(flask.url_for('home'))


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('Erreur : Pas de fichier')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('Erreur : Pas de fichier')
            return redirect(request.url)
        if file and '.' in file.filename and file.filename.rsplit('.', 1)[1] == 'ico':
            filename = "favicon.ico"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return flask.redirect(flask.url_for('home'))
        else:
            if '.' in file.filename:
                flash("Erreur : l'extension est " +
                    file.filename .rsplit('.', 1)[1] +" au lieu de .ico")
                return redirect(request.url)
            else:
                flash("Erreur : le fichier n'a pas d'extension, or l'extension dois être .ico")
                return redirect(request.url)
    return flask.render_template("upload_favico.html.jinja2")


@app.errorhandler(404)
def not_found(e):
    return flask.render_template("404.html.jinja2"), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))