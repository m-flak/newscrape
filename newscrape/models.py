from flask_login import UserMixin
from flask_restful import Resource
from sqlalchemy import text
from sqlalchemy.schema import ForeignKey
import newscrape as ns

class User(UserMixin, ns.db.Model):
    __tablename__ = 'users'
    id       = ns.db.Column(ns.db.Integer, primary_key=True)
    email    = ns.db.Column(ns.db.String(255), index=True, unique=True)
    name     = ns.db.Column(ns.db.String(255), index=True, unique=True)
    password = ns.db.Column('pass', ns.db.LargeBinary)
    admin    = ns.db.Column(ns.db.Boolean)
    keywords = ns.db.relationship('Keyword', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {} via {}>'.format(self.name,self.email)

    def check_password(self, check_pw):
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

    def get_keywords(self):
        return [kw.keyword for kw in Keyword.query.filter_by(user=self).all()]

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
