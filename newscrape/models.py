import base64
from datetime import datetime, timedelta
from itsdangerous.signer import Signer
from flask_login import UserMixin
from flask import current_app
from sqlalchemy import text
from sqlalchemy.schema import ForeignKey
from newscrape.utils import validate_inputs
import newscrape as ns

class User(UserMixin, ns.db.Model):
    __tablename__ = 'users'
    id         = ns.db.Column(ns.db.Integer, primary_key=True)
    email      = ns.db.Column(ns.db.String(255), index=True, unique=True)
    name       = ns.db.Column(ns.db.String(255), index=True, unique=True)
    password   = ns.db.Column('pass', ns.db.LargeBinary)
    admin      = ns.db.Column(ns.db.Boolean)
    keywords   = ns.db.relationship('Keyword', backref='user', lazy='dynamic')
    api_key    = ns.db.Column(ns.db.Text)
    key_expire = ns.db.Column(ns.db.DateTime)
    stories    = ns.db.relationship('SavedStory', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {} via {}>'.format(self.name,self.email)

    def check_password(self, check_pw):
        try:
            check_me = check_pw.decode('utf-8') if isinstance(check_pw,bytes) else check_pw
            validate_inputs(check_me, r"\)|'|;|!|\||\\|,")
        except ValueError:
            return False

        result = ns.db.engine.execute(text('CALL verify_user_password(:u_name, :pw)'),
                    u_name=self.name, pw=check_pw).fetchall()

        if result[0][0] is not None:
            return True
        return False

    def change_password(self, new_pw):
        # jesus, sqlalchemy is so picky with stored procedures
        # # previous, just works, BUT THIS ONE
        # # needs a raw connection
        conn = ns.db.engine.raw_connection()
        try:
            cursor = conn.cursor()
            cursor.callproc('update_user_password',[self.name,new_pw])
            cursor.close()
            conn.commit()
        finally:
            conn.close()

    def gen_api_key(self):
        signer = Signer(base64.b64decode(current_app.secret_key),self.name)
        self.api_key = base64.b64encode(signer.sign('API_KEY'))
        ns.db.session.commit()

    def get_api_key(self):
        if self.api_key is None:
            self.gen_api_key()
        if datetime.now() > self.key_expire:
            newtime = datetime.now() + timedelta(hours=2)
            self.key_expire = newtime.isoformat(' ')[:19]
            ns.db.session.commit()
        return self.api_key

    def get_keywords(self):
        return [kw.keyword for kw in Keyword.query.filter_by(user=self).all()]

    def get_saved_stories(self):
        return SavedStory.query.filter_by(user=self).all()

@ns.login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Keyword(ns.db.Model):
    __tablename__ = 'keywords'
    id      = ns.db.Column(ns.db.Integer, primary_key=True)
    uid     = ns.db.Column('user', ns.db.Integer, ForeignKey('users.id'))
    keyword = ns.db.Column(ns.db.String(32))

    def __repr__(self):
        return "<Keyword '{}'>".format(self.keyword)

class SavedStory(ns.db.Model):
    __tablename__ = 'saved_stories'
    id       = ns.db.Column(ns.db.Integer, primary_key=True)
    uid      = ns.db.Column('user', ns.db.Integer, ForeignKey('users.id'))
    storyid  = ns.db.Column(ns.db.String(64), index=True, unique=True)
    link     = ns.db.Column(ns.db.Text)
    headline = ns.db.Column(ns.db.Text)
    summary  = ns.db.Column(ns.db.Text)

    def __repr__(self):
        return "<SavedStory '{}'>".format(self.storyid)

    def make_dict(self):
        return dict({
                    'id': self.storyid,
                    'link': self.link,
                    'headline': self.headline,
                    'summary': self.summary,
        })
