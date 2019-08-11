import base64
import werkzeug.urls
from flask import (
Blueprint, render_template, request, abort, flash, redirect, url_for,
current_app
)
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy import text
from newscrape.utils import validate_inputs, empty_params, url_is_route
from newscrape.main.forms import (
AdminUsers, admin_user_details, UserUpdatePassword
)
import newscrape as ns

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
@main.route('/index')
@login_required
def index():
    # api keys are good for 2hrs
    # meaning no refresh required for 2hrs :)
    apikey = current_user.get_api_key()
    return render_template('home.html', keywords=current_user.get_keywords(),
                            apikey=werkzeug.urls.url_fix(apikey))

@main.route('/welcome')
def welcome():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    return render_template('welcome.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        # insure passed params are sanitary
        try:
            validate_inputs([request.form['email'],request.form['pass']], r"\)|'|;|!|\||\\|,")
        except ValueError:
            abort(400)
        if empty_params(request.form['email'], request.form['pass']) is True:
            abort(400)
        # verify username & password
        user = ns.models.User.query.filter_by(email=request.form['email']).first()
        if user is None or not user.check_password(base64.b64decode(request.form['pass'])):
            flash("Username/Password invalid!")
            return redirect(url_for('main.login', next=request.form['next']))
        login_user(user)
        next_page = request.form['next']
        if not next_page or not url_is_route(current_app, next_page):
            next_page = url_for('main.index')
        flash("Login was successful!")
        return redirect(next_page)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/register/', methods=['GET', 'POST'])
def register_account():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        email = request.form['email']
        user  = request.form['name']
        reg   = request.form['register']
        pw    = request.form['pass']

        # don't allow illegal characters
        try:
            validate_inputs([email,user,pw], r"\)|'|;|!|\||\\|,")
        except ValueError:
            abort(400)
        # don't allow empty strings
        if empty_params(email, user, pw) is True:
            abort(400)

        # is username / email already registered?
        result = ns.db.session.execute(
            'SELECT email,name FROM users WHERE name=:u_name OR email=:e_mail',
            {'u_name': user, 'e_mail': email,}
        )
        # create account if not already registered
        if result.rowcount > 0:
            # exists, don't create
            reg = "no"
        else:
            pwhash = ns.db.session.execute(
                'SELECT CAST(SHA2(:pass, 512) AS CHAR)',
                {'pass': base64.b64decode(pw),}).fetchone()[0]

            # apparently, you need to use engine.execute to write to the DB
            ns.db.engine.execute(text(
                'INSERT INTO users (email,name,pass) VALUES(:e_mail,:u_name,AES_ENCRYPT(:passw,:pass_hash))'),
                e_mail=email, u_name=user, passw=base64.b64decode(pw), pass_hash=pwhash)

        return render_template('register.html', reg=reg)

@main.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.admin is not True:
        abort(403)

    form = AdminUsers()
    if form.validate_on_submit():
        subforms = [u for u in form.user_details.entries if u.update_user.data is True]
        if len(subforms) > 0:
            for subform in subforms:
                subform.update_changed()
                flash("{}: User information updated.".format(subform.old_name.data))
        else:
            flash("No users to be updated.")
        return redirect(url_for('main.admin'))
    elif request.method == 'GET':
        for ud in admin_user_details(ns.models.User.query.count()):
            form.user_details.append_entry(ud)

    return render_template('admin.html', form=form)

@main.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    if current_user.admin is True:
        return redirect(url_for('main.admin'))

    form = UserUpdatePassword()
    if form.validate_on_submit():
        if not current_user.check_password(form.cur_pass.data):
            flash("Please enter your current password correctly.")
        else:
            current_user.change_password(form.new_pass2.data)
            flash("Password updated successfully.")
        return redirect(url_for('main.user'))

    return render_template('user.html', form=form)

@main.route('/saved')
@login_required
def saved():
    apikey = current_user.get_api_key()
    saved_stories = [ss.make_dict() for ss in current_user.get_saved_stories()]

    return render_template('saved.html', apikey=werkzeug.urls.url_fix(apikey),
                            saved_stories=saved_stories)
